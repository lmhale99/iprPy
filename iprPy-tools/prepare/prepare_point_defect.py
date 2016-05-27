import os
import uuid
import atomman as am
import atomman.lammps as lmp
from gen_element_pairings import *
from DataModelDict import DataModelDict
import glob
import shutil

def point_defect(terms, 
                 lammps_exe, xml_library_dir, iprPy_dir,
                 defined_element, potentials, potential_directories, 
                 crystals, crystal_elements,
                 u_length, u_press, u_energy):
                     
    """Prepares structure static calculations."""
    assert lammps_exe is not None, 'No lammps_exe set'
    assert xml_library_dir is not None, 'No xml_library_dir set'
    assert len(potentials) > 0, 'No potentials given'
    assert len(potentials) == len(potential_directories), 'Mismatching lengths of potentials and directories'
    assert len(crystals) > 0, 'No crystals given'
    assert len(crystals) == len(crystal_elements), 'Mismatching lengths of crystals and elements'

    for pot, pot_dir, symbols, crystal in gen_element_pairings(defined_element, 
                                                               potentials, potential_directories, 
                                                               crystals, crystal_elements):
        
        with open(pot) as f:
            potential = DataModelDict(f)
            
        pot_xml_dir = os.path.join(xml_library_dir, potential['LAMMPS-potential']['potential']['id'], 'structure_static', 'standard')
        if not os.path.isdir(pot_xml_dir):
            os.makedirs(pot_xml_dir)
        
        match = False
        for fname in glob.iglob(os.path.join(pot_xml_dir, '*.xml')):
            pot_match = False
            crystal_match = False
            symbol_match = False
            with open(fname) as f:
                test_model = DataModelDict(f)
            if potential['LAMMPS-potential']['potential']['key'] == test_model['calculation-crystal-phase']['potential']['key']:
                pot_match = True
            if os.path.basename(crystal) == test_model['calculation-crystal-phase']['crystal-info']['artifact']:               
                crystal_match = True
            symbols2 = test_model['calculation-crystal-phase']['crystal-info'].aslist('symbols')
            if len(symbols) == len(symbols2):
                symbol_match = True
                for sy1, sy2 in zip(symbols, symbols2):
                    if sy1 != sy2: 
                        symbol_match = False
                        break

            if (pot_match and crystal_match and symbol_match):
                match = True
                break
        if not match:
        
            UUID = str(uuid.uuid4())
            
            with open(crystal) as f:
                try:
                    ucell = am.models.crystal(f)[0]
                except:
                    ucell = am.models.cif_cell(f)[0]
            
            model = DataModelDict()
            model['calculation-crystal-phase'] = calc = DataModelDict()
            
            calc['calculation-id'] = UUID
            calc['potential'] = potential['LAMMPS-potential']['potential']
            
            calc['crystal-info'] = DataModelDict()
            calc['crystal-info']['artifact'] = os.path.basename(crystal)
            calc['crystal-info']['symbols'] = symbols
            
            calc['phase-state'] = DataModelDict()
            calc['phase-state']['temperature'] = DataModelDict([('value', 0.0), ('unit', 'K')])
            calc['phase-state']['pressure'] = DataModelDict([('value', 0.0), ('unit', u_press)])
            
            calc['as-constructed-atomic-system'] = ucell.model(symbols=symbols, box_unit=u_length)
            
            with open(os.path.join(pot_xml_dir, UUID+'.xml'), 'w') as f:
                model.xml(fp=f, indent=4)
            
            r_min = 2.0
            r_max = 5.0
            steps = 100
            if 'r_range' in terms:
                i = terms.index('r_range')
                r_min = float(terms[i+1])
                r_max = float(terms[i+2])
            if 'steps' in terms:
                i = terms.index('steps')
                steps = int(terms[i+1])
            
            sim_dir = os.path.join(os.getcwd(), UUID)
            os.mkdir(sim_dir)
            shutil.copy(pot, sim_dir)
            shutil.copy(crystal, sim_dir)
            shutil.copy(os.path.join(iprPy_dir, 'calculation', 'calc_structure_static.py'), sim_dir)
            if pot_dir != '':
                os.mkdir(os.path.join(sim_dir, os.path.basename(pot_dir)))
                for fname in glob.iglob(os.path.join(pot_dir, '*')):
                    shutil.copy(fname, os.path.join(sim_dir, os.path.basename(pot_dir) ) )
            
            with open(os.path.join(sim_dir, 'calc_structure_static.in'), 'w') as f:
                f.write( '\n'.join(['lammps_exe                 %s' % lammps_exe,
                                    '',
                                    'potential_file             %s' % os.path.basename(pot),
                                    'potential_dir              %s' % os.path.basename(pot_dir),
                                    '',
                                    'crystal_file               %s' % os.path.basename(crystal),
                                    'symbols                    %s' % ' '.join(symbols),
                                    '',
                                    'r_min                      %s' % repr(r_min),
                                    'r_max                      %s' % repr(r_max),
                                    'steps                      %i' % steps,
                                    '',
                                    'length_display_units       %s' % u_length,
                                    'pressure_display_units     %s' % u_press,
                                    'energy_display_units       %s' % u_energy]) )
             


            