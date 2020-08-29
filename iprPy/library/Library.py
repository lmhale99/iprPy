# coding: utf-8
# Standard Python libraries
from pathlib import Path
import uuid

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# https://github.com/usnistgov/atomman
import atomman as am

import requests

from .. import load_record
from ..tools import aslist

class Library(am.library.Database):
    """
    Class for interacting with potential records hosted from potentials.nist.gov
    """

    def download_refs(self, style=None, status='active', format='json', indent=4, verbose=False):
        """
        Downloads reference records from potentials.nist.gov to the library.
        Note: this will overwrite any local copies of records with matching
        names.  If you made changes to library files, be sure to save them
        with a different name.

        Parameters
        ----------
        style : str or list, optional
            The reference style(s) to download.  If not given, all reference
            style will be downloaded.
        status : str, list or None, optional
            Only the potential_LAMMPS records with the given status(es) will
            be downloaded.  Allowed values are 'active' (default),
            'superseded', and 'retracted'.  If set to None, all hosted
            potential_LAMMPS will be downloaded.
        """
        assert format in ['json', 'xml']
        
        # use all_ref_styles if none are specified
        all_ref_styles = ['crystal_prototype', 'dislocation', 'free_surface',
                          'point_defect', 'stacking_fault', 'potential_LAMMPS']
        
        if style is None:
            style = all_ref_styles
        style = aslist(style)
        
        for s in style:
            if s == 'potential_LAMMPS':
                self.download_lammps_potentials(format=format, indent=indent,
                                                      status=status, verbose=verbose)
            else:
                self.download_records(s, format=format, indent=indent, verbose=verbose)

    def download_oqmd_crystals(self, elements, localpath=None, format='json', indent=4):
        """
        Accesses OQMD and downloads crystal structures containing the given
        elements.  The structures are saved to the iprPy library as
        reference_crystal records.
        
        Parameters
        ----------
        elements : list
            A list of element symbols.
        """
        assert format in ['json', 'xml']

        # Load record style and set universal values
        style = 'reference_crystal'
        record = load_record(style)
        input_dict = {}
        input_dict['sourcename'] = "Open Quantum Materials Database"
        input_dict['sourcelink'] = "http://oqmd.org/"
        input_dict['length_unit'] = "angstrom"
        
        # Set library subdirectory
        if localpath is None:
            localpath = self.localpath
        style_directory = Path(localpath, style)
        if not style_directory.is_dir():
            style_directory.mkdir(parents=True)
        
        # Sort elements
        elements.sort()

        # Build list of downloaded entries
        have = []
        for fname in style_directory.glob('oqmd-*.*'):
            have.append(fname.stem)
        
        # Build list of missing OQMD entries
        elements_string = '-'.join(elements)
        
        composition_r = requests.get('http://oqmd.org/materials/composition/' + elements_string)
        composition_html = composition_r.text
        
        missing = []
        count = 0
        while True:
            count += 1
            try:
                start = composition_html.index('href="/materials/entry/') + len('href="/materials/entry/')
            except:
                break
            else:
                end = start + composition_html[start:].index('"')
                entry_number = composition_html[start:end]
                composition_html = composition_html[end+2:]
                entry_id = f'oqmd-{entry_number}'
                if entry_id not in have and entry_id not in missing:
                    missing.append(entry_id)
            if count > 100:
                raise ValueError('Loop likely infinite')
        
        # Download missing entries
        for entry_id in missing:
            entry_number = entry_id.replace('oqmd-', '')
            entry_r = requests.get('http://oqmd.org/materials/entry/' + entry_number)
            entry_html = entry_r.text
            
            start = entry_html.index('href="/materials/structure/') + len('href="/materials/structure/')
            end = start + entry_html[start:].index('"')
            structure_number = entry_html[start:end]
            
            try:
                structure_url = 'http://oqmd.org/materials/export/conventional/poscar/' + structure_number
                structure_r = requests.get(structure_url)
                structure_r.raise_for_status()
            except:
                try:
                    structure_url = 'http://oqmd.org/materials/export/primitive/poscar/' + structure_number
                    structure_r = requests.get(structure_url)
                    structure_r.raise_for_status()
                except:
                    continue
            
            # Build record content
            input_dict['id'] = entry_id
            input_dict['ucell'] = am.load('poscar', structure_r.text).normalize()
            record.buildcontent(input_dict)

            # Save
            with open(Path(style_directory, f'{entry_id}.{format}'), 'w') as f:
                if format == 'json':
                    record.content.json(fp=f, indent=indent)
                else:
                    record.content.xml(fp=f, indent=indent)
            print('Added', entry_id)

    def download_mp_crystals(self, elements, api_key=None, localpath=None, format='json', indent=4):
        """
        Accesses Materials Project and downloads crystal structures containing the given
        elements.  The structures are saved to the iprPy library as
        reference_crystal records.
        
        Parameters
        ----------
        elements : list
            A list of element symbols.
        api_key : str, optional
            The user's Materials Project API key. If not given, will use "MAPI_KEY"
            environment variable
        """

        assert format in ['json', 'xml']

        # Function-specific imports
        import pymatgen as pmg
        from pymatgen.ext.matproj import MPRester
        
        # Define subset generator
        def subsets(fullset):
            """Yields element combination subsets"""
            for i, item in enumerate(fullset):
                yield [item]
                if len(fullset) > 1:
                    for subset in subsets(fullset[i+1:]):
                        yield [item] + subset

        # Load record style and set universal values
        style = 'reference_crystal'
        record = load_record(style)
        input_dict = {}
        input_dict['sourcename'] = "Materials Project"
        input_dict['sourcelink'] = "https://materialsproject.org/"
        input_dict['length_unit'] = "angstrom"

        # Set library subdirectory
        if localpath is None:
            localpath = self.localpath
        style_directory = Path(localpath, style)
        if not style_directory.is_dir():
            style_directory.mkdir(parents=True)
        
        # Sort elements
        elements.sort()

        # Build list of downloaded entries
        have = []
        for fname in style_directory.glob('mp-*.*'):
            have.append(fname.stem)
        
        # Open connection to Materials Project
        with MPRester(api_key) as m:
            
            # Loop over subsets of elements
            for subelements in subsets(elements):
                
                # Query MP for all entries corresponding to the elements
                entries = m.query({"elements": subelements}, ["material_id"])
                
                # Add entries to the list if not there
                missing = []
                for entry in entries:
                    if entry['material_id'] not in have and entry['material_id'] not in missing:
                        missing.append(entry['material_id'])
                
                # Download missing entries
                try:
                    entries = m.query({"material_id": {"$in": missing}}, ['material_id', 'cif'])
                except:
                    pass
                else:
                    # Convert cif to model and save
                    for entry in entries:
                        entry_id = entry['material_id']
                        struct = pmg.Structure.from_str(entry['cif'], fmt='cif')
                        struct = pmg.symmetry.analyzer.SpacegroupAnalyzer(struct).get_conventional_standard_structure()
                        
                        # Build record content
                        input_dict['id'] = entry_id
                        input_dict['ucell'] = am.load('pymatgen_Structure', struct).normalize()
                        record.buildcontent(input_dict)

                        # Save
                        with open(Path(style_directory, f'{entry_id}.{format}'), 'w') as f:
                            if format == 'json':
                                record.content.json(fp=f, indent=indent)
                            else:
                                record.content.xml(fp=f, indent=indent)
                        print('Added', entry_id)

    def get_ref(self, style, name, verbose=False, asrecord=True):
        """
        Gets a reference file from the iprPy library or by downloading from
        potentials.nist.gov if a local copy is not found.
        
        Parameters
        ----------
        style : str
            The reference record's style.
        name : str
            The name of the record.
        verbose: bool, optional
            If True, informative print statements will be used.
        asrecord : bool, optional
            If True (default) then the content will be returned as an iprPy
            Record if a subclass has been defined for the style.
            
        Returns
        -------
        iprPy.Record
            The content as an iprPy Record object. Returned if asrecord is True
            and iprPy has a subclass for the record's style.
        DataModelDict.DataModelDict
            The content as a DataModelDict.  Returned if asrecord is False or
            iprPy does not have a subclass for the record's style.
        """
        content = self.get_record(template=style, title=name, verbose=verbose)
                
        # Load as iprPy record if style exists
        try:
            assert asrecord
            return load_record(style, name, content)
        except:
            return content
