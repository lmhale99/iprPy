# coding: utf-8

# Standard Python libraries
from pathlib import Path
from copy import deepcopy

# http://www.numpy.org/
import numpy as np

# https://pandas.pydata.org/
import pandas as pd

import matplotlib.pyplot as plt

import atomman.unitconvert as uc

# Local imports
from ... import load_record

def stacking(self, 
             upload: bool = True,
             runall: bool = False):
    """
    Main function for processing stacking_fault_map_2D calculations as used
    for building the content hosted on the NIST Interatomic Potentials
    Repository.
    
    Processing steps:
    
    1. calculation_stacking_fault_map_2D records are retrieved from the database.
    2. Plots are generated for the plane and directions.
    3. If path info exists, then plots with mep are generated.
    4. Plot names added to PotentialProperties, and tabulated values
    5. Raw gamma records are saved in json format.
    
    Parameters
    ----------
    upload : bool, optional
        If True (default) then the new/modified PotentialProperties records
        will be uploaded to the database automatically.
    runall : bool, optional
        If True, all plots and tables will be regenerated.  If False, only new
        ones are created.  Default value is False.
    """
    # Class attributes
    database = self.database
    getkwargs = self.getkwargs
    outputpath = self.outputpath
    props = self.props
    prop_df = self.prop_df()

    # Get records and records_df
    records, records_df = database.get_records(style='calculation_stacking_fault_map_2D',
                                               status='finished', return_df=True,
                                               **getkwargs)
    
    # Link record objects to df
    allgamma = []
    allpaths = []
    for i in records_df.index:
        allgamma.append(records[i].gamma)
        try:
            paths = records[i].paths
        except:
            paths = []
        allpaths.append(paths)
    records_df['gamma'] = allgamma
    records_df['paths'] = allpaths

    # Load parent records
    parents_df = self.crystals_df

    # Add prototype field
    self.identify_prototypes(records_df)

    # Extract plane field from stackingfault_id
    def assign_plane(series):
        fault = series.stackingfault_id.replace(f'{series.family}--', '')
        if '-' in fault:
            plane, pslice = fault.split('sf-')
            return f'({plane}) {pslice}'
        else:
            return f'({fault.strip("sf")})'
    records_df['plane'] = records_df.apply(assign_plane, axis=1)

    # Merge parent data into records
    records_df = records_df.merge(parents_df, left_on='parent_key', right_on='key',
                                suffixes=('', '_parent'), validate='many_to_one')
    
    num_updated = 0
    num_skipped = 0
    newprops = []
    for imp_df, pot_id, pot_key, imp_id, imp_key in self.iter_imp_df(records_df):

        # Get or init a properties record
        matching_props = props[(prop_df.potential_LAMMPS_key == imp_key) & (prop_df.potential_key == pot_key)]
        if len(matching_props) == 1:
            prop = matching_props[0]
        elif len(matching_props) == 0:
            prop = load_record('PotentialProperties', potential_key=pot_key,
                               potential_id=pot_id, potential_LAMMPS_key=imp_key,
                               potential_LAMMPS_id=imp_id)
            prop.build_model()
            newprops.append(prop)
        else:
            print('multiple prop records found!')
            continue

        # Skip records with existing results
        if prop.stackingfaults.exists and runall is False:
            print('skipped')
            num_skipped += 1
            continue

        # Build contentpath and check if it exists
        contentpath = Path(outputpath, pot_id, imp_id)
        if not contentpath.is_dir():
            contentpath.mkdir(parents=True)

        # Set imp data to prop
        prop.stackingfaults.data = transform_imp_df(imp_df)

        # Build plots and set plot data to prop
        prop.stackingfaults.plot = stacking_pyplot_plots(imp_df, outputpath, pot_id, imp_id)

        # Build model component
        prop.stackingfaults.exists = True
        model = prop.model['per-potential-properties']
        prop.stackingfaults.build_model(model)

        # Add/update PotentialsProperties record
        if upload:
            try:
                database.add_record(prop)
                print('added to database')
            except:
                database.update_record(prop)
                print('updated in database')
        else:
            print('created/modified')
        num_updated += 1

    if len(newprops) > 0:
        self.add_props(newprops)
    print(num_updated, 'added/updated')
    print(num_skipped, 'skipped')

def transform_imp_df(imp_df):
    """
    Transform imp_df to the form used by the PotentialProperties records 
    """
    new_df = []
    for i in imp_df.index:
        series = imp_df.loc[i]

        # Build results
        dat = {}
        dat['composition'] = series.composition
        dat['prototype'] = series.prototype
        dat['a'] = series.a
        dat['plane'] = series.plane
        
        # Add intrinsic fault energy
        if pd.notna(series.E_isf):
            dat['measurement'] = 'E_isf'
            dat['value'] = uc.get_in_units(series.E_isf, 'mJ/m^2')
            new_df.append(dat)
            dat = deepcopy(dat)
        
        # Add unstable fault energies and ideal shears
        for key in imp_df:
            if 'E_usf_mep' in key and pd.notna(series[key]):
                dat['measurement'] = key.replace('_mep', '')
                dat['value'] = uc.get_in_units(series[key], 'mJ/m^2')
                new_df.append(dat)
                dat = deepcopy(dat)
        
        # Add ideal shears
        for key in imp_df:        
            if 'τ_ideal_mep' in key and pd.notna(series[key]):
                dat['measurement'] = key.replace('_mep', '')
                dat['value'] = uc.get_in_units(series[key], 'GPa')
                new_df.append(dat)
                dat = deepcopy(dat)
            
    new_df = pd.DataFrame(new_df)

    return new_df

def stacking_pyplot_plots(df, outputpath, potential, implementation):
    
    surface_energy_units = 'mJ/m^2'
    
    # Set path to directory
    contentpath = Path(outputpath, potential, implementation)
    
    # Init list for plot_df
    plot_df = []
    
    # Loop over entries
    for i in df.index:
        series = df.loc[i]
        
        # Get gamma
        gamma = series.gamma
        
        # Build base filename from composition, fault id and record key
        basetag = f'stackingfault.{series.composition}.{series.stackingfault_id}.{series.key}'

        # Save data model
        jsonname = f'{basetag}.json'
        with open(Path(contentpath, jsonname), 'w', encoding='UTF-8') as f:
            gamma.model().json(fp=f, ensure_ascii=False)
        
        # Build dict with common fields
        dat = {}
        dat['composition'] = series.composition
        dat['prototype'] = series.prototype
        dat['a'] = series.a
        dat['plane'] = series.plane
        dat['name'] = None
        dat['png'] = None
        dat['json'] = jsonname
        
        # Get vects for plotting
        vects = get_plotvects(gamma.a1vect, gamma.a2vect, series.stackingfault_id)
        
        # Generate 2D surface
        plotname = f'{basetag}.2D.png'
        gamma.E_gsf_surface_plot(a1vect=vects['2Dvects'][0],
                                 a2vect=vects['2Dvects'][1],
                                 energyperarea_unit=surface_energy_units)
        plt.savefig(Path(contentpath, plotname), bbox_inches='tight')
        plt.close()
        dat['name'] = series.plane
        dat['png'] = plotname
        plot_df.append(dat)
        dat = deepcopy(dat)

        # Loop over paths
        for path in series.paths:
            direction = path.direction
            if path.coord is None:
                continue
            dirnums = direction[direction.index('[')+1:].strip(']').replace('-', '').replace(' ', '')
            # Generate 2D plot to add mep to
            plotname = f'{basetag}.2D.{dirnums}.png'
            gamma.E_gsf_surface_plot(a1vect=vects['2Dvects'][0],
                                        a2vect=vects['2Dvects'][1],
                                        energyperarea_unit=surface_energy_units)

            # Rotate coords to match plot rotation
            angle = vects['angle'] * np.pi / 180
            x = path.coord[:, 0] * np.cos(angle) - path.coord[:, 1] * np.sin(angle)
            y = path.coord[:, 0] * np.sin(angle) + path.coord[:, 1] * np.cos(angle)

            # Translate mep by a1 or a2 if needed
            if series.stackingfault_id in ['A1--Cu--fcc--111sf', 'A3--Mg--hcp--0001sf']:
                dx, dy = gamma.a12_to_xy(1.0, 0.0, a1vect=vects['2Dvects'][0], a2vect=vects['2Dvects'][1])
                x += dx
                y += dy
            elif series.stackingfault_id == 'A3--Mg--hcp--1011sf-2' and dirnums == '1210':
                dx, dy = gamma.a12_to_xy(0.0, 1.0, a1vect=vects['2Dvects'][0], a2vect=vects['2Dvects'][1])
                x += dx
                y += dy

            plt.plot(x, y, 'ro:')        
            plt.savefig(Path(contentpath, plotname), bbox_inches='tight')
            plt.close()
            dat['name'] = f'{series.plane} - mep {direction}'.strip()
            dat['png'] = plotname
            plot_df.append(dat)
            dat = deepcopy(dat)

        # Generate 1D a1 plot
        plotname = f'{basetag}.a1.png'
        gamma.E_gsf_line_plot(vect=vects['a1vect'], energyperarea_unit=surface_energy_units)
        plt.savefig(Path(contentpath, plotname), bbox_inches='tight')
        plt.close()
        dat['name'] = f'{series.plane} - {vects["a1vect"]}'.strip()
        dat['png'] = plotname
        plot_df.append(dat)
        dat = deepcopy(dat)
        
        # Generate 1D a1 plot
        plotname = f'{basetag}.a2.png'
        gamma.E_gsf_line_plot(vect=vects['a2vect'], energyperarea_unit=surface_energy_units)
        plt.savefig(Path(contentpath, plotname), bbox_inches='tight')
        plt.close('all')
        dat['name'] = f'{series.plane} - {vects["a2vect"]}'.strip()
        dat['png'] = plotname
        plot_df.append(dat)
        dat = deepcopy(dat)

    return pd.DataFrame(plot_df)

def get_plotvects(a1vect, a2vect, stackingfault_id):
    vects = {}

    # Specify replacements when a1vect equivalent to a2vect
    if (stackingfault_id == 'A1--Cu--fcc--100sf' or
        stackingfault_id == 'A2--W--bcc--110sf'):
        vects['a2vect'] = a1vect + a2vect

    # Convert fcc-111/hcp-0001 to standard orthogonal cell representation
    elif (stackingfault_id == 'A1--Cu--fcc--111sf'):
        vects['a1vect'] = a1vect - 2 * a2vect
        vects['a2vect'] = a1vect
        vects['2Dvects'] = (vects['a1vect'], vects['a2vect'])
        vects['angle'] = 90.0
        
    elif (stackingfault_id == 'A3--Mg--hcp--0001sf'):
        vects['a1vect'] = a1vect - 2 * a2vect
        vects['a2vect'] = a1vect
        vects['2Dvects'] = (vects['a1vect'], vects['a2vect'])
        vects['angle'] = 90.0
    
    # Set defaults
    vects['a1vect'] = vects.get('a1vect', a1vect)
    vects['a2vect'] = vects.get('a2vect', a2vect)
    vects['2Dvects'] = vects.get('2Dvects', (a1vect, a2vect))
    vects['angle'] = vects.get('angle', 0.0)

    return vects