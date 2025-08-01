# coding: utf-8

# Standard Python libraries
from pathlib import Path
from datetime import date
from math import floor, ceil
from copy import deepcopy

# http://www.numpy.org/
import numpy as np

# https://pandas.pydata.org/
import pandas as pd

# https://plotly.com/python
import plotly.graph_objects as go

from atomman import Box, ElasticConstants2
import atomman.unitconvert as uc

# Local imports
from ... import load_record



def mdthermo(self,
             upload: bool = True,
             runall: bool = False):
    """
    Main function for processing the thermodynamic data from
    md_solid_properties and md_liquid_properties records as used for building
    the content hosted on the NIST Interatomic Potentials Repository.
    
    Processing steps:
    
    1. md_solid_properties and md_liquid_properties records are retrieved from
       the database.
    2. Tables of data and Bokeh plots are constructed for each potential
       implementation.
    3. Details added to PotentialProperties records to indicate plots exist.
    
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
    getkwargs = deepcopy(self.getkwargs)
    outputpath = self.outputpath
    props = self.props
    prop_df = self.prop_df()

    # Parse props based on getkwargs if needed
    mask = np.ones(len(props), dtype=bool)
    if 'potential_LAMMPS_id' in getkwargs:
        mask = (mask) & (prop_df.potential_LAMMPS_id == getkwargs['potential_LAMMPS_id'])
        del getkwargs['potential_LAMMPS_id']
    if 'potential_LAMMPS_key' in getkwargs:
        mask = (mask) & (prop_df.potential_LAMMPS_key == getkwargs['potential_LAMMPS_key'])
        del getkwargs['potential_LAMMPS_key']
    if 'potential_id' in getkwargs:
        mask = (mask) & (prop_df.potential_id == getkwargs['potential_id'])
        del getkwargs['potential_id']
    if 'potential_key' in getkwargs:
        mask = (mask) & (prop_df.potential_key == getkwargs['potential_key'])
        del getkwargs['potential_key']
    if mask.sum() != len(props):
        props = props[mask]
        prop_df = prop_df[mask].reset_index(drop=True)

    # Loop over all props
    num_updated = 0
    num_skipped = 0
    for i, prop in enumerate(props):

        pot_id = prop.potential_id
        pot_key = prop.potential_key
        imp_id = prop.potential_LAMMPS_id
        imp_key = prop.potential_LAMMPS_key
        print(i, pot_id, imp_id, end=' ')
    
        # Skip records with existing results
        if prop.mdthermo.exists and runall is False:
            print('skipped')
            num_skipped += 1
            continue
    
        # Get solid and liquid results
        getkwargs['potential_key'] = pot_key
        getkwargs['potential_LAMMPS_key'] = imp_key
        all_solid_df = database.get_records_df(style='md_solid_properties',
                                            **getkwargs)
        all_liquid_df = database.get_records_df(style='md_liquid_properties',
                                            **getkwargs)

        if len(all_solid_df) == 0 and len(all_liquid_df) == 0:   
            print('no finished records found')
            continue   

        # Add prototype field to solid data
        self.identify_prototypes(all_solid_df)

        compositions = np.unique(all_solid_df.composition.tolist() + all_liquid_df.composition.tolist())
        
        # Loop over compositions
        thermoplot = []
        for composition in compositions:
            solid_df = all_solid_df[all_solid_df.composition == composition]
            liquid_df = all_liquid_df[all_liquid_df.composition == composition]

            # Build and save plots and tables
            self.mdthermo_plots(solid_df, liquid_df, outputpath, pot_id, imp_id,
                                composition, thermoplot)
        
        # Build info tables for the extracted/generated plots
        prop.mdthermo.thermoplot = pd.DataFrame(thermoplot)

        # Build model component
        prop.mdthermo.exists = True
        model = prop.model['per-potential-properties']
        prop.mdthermo.build_model(model)

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
        
    print(num_updated, 'added/updated')
    print(num_skipped, 'skipped')

def mdthermo_plots(self,
                   solid_df,
                   liquid_df,
                   outputpath: Path,
                   potential: str,
                   implementation: str,
                   composition,
                   data):
    """
    Function to call all plot generation functions for thermo data.
    """
    contentpath = Path(outputpath, potential, implementation)
    if not contentpath.exists():
        contentpath.mkdir(parents=True)


    self.mdthermo_energy_plot(solid_df, liquid_df, composition, contentpath, data,
                              uc_unit='eV', plot_unit='eV/atom')
    self.mdthermo_gibbs_plot(solid_df, liquid_df, composition, contentpath, data,
                             uc_unit='eV', plot_unit='eV/atom')
    self.mdthermo_entropy_plot(solid_df, liquid_df, composition, contentpath, data,
                               uc_unit='J/mol', plot_unit='J/K/mol')
    self.mdthermo_cp_plot(solid_df, liquid_df, composition, contentpath, data,
                          uc_unit='J/mol', plot_unit='J/K/mol')
    self.mdthermo_volume_plot(solid_df, liquid_df, composition, contentpath, data,
                              uc_unit='angstrom^3', plot_unit='&#197;^3/atom')


def mdthermo_energy_plot(self,
                         solid_df,
                         liquid_df,
                         composition,
                         contentpath,
                         data,
                         uc_unit='eV',
                         plot_unit='eV/atom'):
    
    # Initialize plot and table
    fig = go.Figure()
    pngfile = f'mdthermo.{composition}.U.png'
    csvfile = f'mdthermo.{composition}.U.csv'
    htmlfile = f'mdthermo.{composition}.U.html'

    lineformats = self.plotly_line_formats

    # Loop over solid prototypes
    values = {}
    Tmax = 0
    for prototype in np.unique(solid_df.prototype):
        proto_df = solid_df[solid_df.prototype == prototype]
        for i, relaxed_crystal_key in enumerate(np.unique(proto_df.relaxed_crystal_key)):
            crystal_df = proto_df[proto_df.relaxed_crystal_key == relaxed_crystal_key]
            if i == 0:
                tag = prototype
            else:
                tag = f'{prototype} ({i+1})'

            parsed_df = crystal_df[crystal_df.untransformed].sort_values('T (K)')
            values[tag] = parsed_df['U (eV/atom)'].values

            if Tmax < parsed_df['T (K)'].values[-1]:
                Tmax = parsed_df['T (K)'].values[-1]
            
    # Add liquid
    if len(liquid_df) > 0:
        sorted_df = liquid_df.sort_values('T (K)')
        v = sorted_df['U (eV/atom)'].values
        v[~liquid_df.isliquid] = np.nan
        values['liquid'] = v

        if Tmax < sorted_df['T (K)'].values[-1]:
            Tmax = sorted_df['T (K)'].values[-1]
    
    # Build table
    table_df = build_table(values, Tmax, uc_unit)
    
    # Loop over results
    for i, tag in enumerate(values.keys()):
                
        lineformat = lineformats.iloc[i]

        # Define plot lines
        fig.add_trace(
            go.Scatter(
                x=table_df.temperature,
                y=table_df[tag],
                mode='lines',
                name=tag,
                showlegend=True,
                line=dict(
                    color=lineformat.color,
                    dash=lineformat.line)))
            
    fig.update_layout(
        title=dict(
            text="Energy vs. Temperature",
            font=dict(size=14),
        ),
        xaxis=dict(
            title=dict(
                text="Temperature (K)"
            )
        ),
        yaxis=dict(
            title=dict(
                text=f"Energy ({plot_unit})"
            )
        ),
        paper_bgcolor='white',
        plot_bgcolor='white',
    )
    fig.update_xaxes(
        range=[0, Tmax],
        **self.plotly_axes_settings
    )
    fig.update_yaxes(
        **self.plotly_axes_settings
    )
    fig.write_image(Path(contentpath, pngfile), width=1200, height=600,) 
    fig.write_html(Path(contentpath, htmlfile), include_plotlyjs='cdn', full_html=False)
    table_df.to_csv(Path(contentpath, csvfile), index=False)

    # Collect data for web generation
    dat = {}
    dat['composition'] = composition
    dat['name'] = 'Energy'
    dat['html'] = htmlfile
    dat['png'] = pngfile
    dat['csv'] = csvfile
    data.append(dat)
            
    fig.data = []

def mdthermo_gibbs_plot(self,
                        solid_df,
                        liquid_df,
                        composition,
                        contentpath,
                        data,
                        uc_unit='eV',
                        plot_unit='eV/atom'):
    
    # Initialize plot and table
    fig = go.Figure()
    pngfile = f'mdthermo.{composition}.G.png'
    csvfile = f'mdthermo.{composition}.G.csv'
    htmlfile = f'mdthermo.{composition}.G.html'

    lineformats = self.plotly_line_formats

    # Loop over solid prototypes
    values = {}
    Tmax = 0
    for prototype in np.unique(solid_df.prototype):
        proto_df = solid_df[solid_df.prototype == prototype]
        for i, relaxed_crystal_key in enumerate(np.unique(proto_df.relaxed_crystal_key)):
            crystal_df = proto_df[proto_df.relaxed_crystal_key == relaxed_crystal_key]
            if i == 0:
                tag = prototype
            else:
                tag = f'{prototype} ({i+1})'

            parsed_df = crystal_df[crystal_df.untransformed].sort_values('T (K)')
            values[tag] = parsed_df['G (eV/atom)'].values

            if Tmax < parsed_df['T (K)'].values[-1]:
                Tmax = parsed_df['T (K)'].values[-1]
            
    # Add liquid
    if len(liquid_df) > 0:
        sorted_df = liquid_df.sort_values('T (K)')
        v = sorted_df['G (eV/atom)'].values
        v[~liquid_df.isliquid] = np.nan
        values['liquid'] = v

        if Tmax < sorted_df['T (K)'].values[-1]:
            Tmax = sorted_df['T (K)'].values[-1]
    
    # Build table
    table_df = build_table(values, Tmax, uc_unit)
    
    # Loop over results
    for i, tag in enumerate(values.keys()):
                
        lineformat = lineformats.iloc[i]

        # Define plot lines
        fig.add_trace(
            go.Scatter(
                x=table_df.temperature,
                y=table_df[tag],
                mode='lines',
                name=tag,
                showlegend=True,
                line=dict(
                    color=lineformat.color,
                    dash=lineformat.line)))
            
    fig.update_layout(
        title=dict(
            text="Gibbs Free Energy vs. Temperature",
            font=dict(size=14),
        ),
        xaxis=dict(
            title=dict(
                text="Temperature (K)"
            )
        ),
        yaxis=dict(
            title=dict(
                text=f"Gibbs ({plot_unit})"
            )
        ),
        paper_bgcolor='white',
        plot_bgcolor='white',
    )
    fig.update_xaxes(
        range=[0, Tmax],
        **self.plotly_axes_settings
    )
    fig.update_yaxes(
        **self.plotly_axes_settings
    )
    fig.write_image(Path(contentpath, pngfile), width=1200, height=600,) 
    fig.write_html(Path(contentpath, htmlfile), include_plotlyjs='cdn', full_html=False)
    table_df.to_csv(Path(contentpath, csvfile), index=False)

    # Collect data for web generation
    dat = {}
    dat['composition'] = composition
    dat['name'] = 'Energy'
    dat['html'] = htmlfile
    dat['png'] = pngfile
    dat['csv'] = csvfile
    data.append(dat)
            
    fig.data = []


def mdthermo_entropy_plot(self,
                         solid_df,
                         liquid_df,
                         composition,
                         contentpath,
                         data,
                         uc_unit='eV',
                         plot_unit='eV/atom'):
    
    # Initialize plot and table
    fig = go.Figure()
    pngfile = f'mdthermo.{composition}.U.png'
    csvfile = f'mdthermo.{composition}.U.csv'
    htmlfile = f'mdthermo.{composition}.U.html'

    lineformats = self.plotly_line_formats

    # Loop over solid prototypes
    values = {}
    Tmax = 0
    for prototype in np.unique(solid_df.prototype):
        proto_df = solid_df[solid_df.prototype == prototype]
        for i, relaxed_crystal_key in enumerate(np.unique(proto_df.relaxed_crystal_key)):
            crystal_df = proto_df[proto_df.relaxed_crystal_key == relaxed_crystal_key]
            if i == 0:
                tag = prototype
            else:
                tag = f'{prototype} ({i+1})'

            parsed_df = crystal_df[crystal_df.untransformed].sort_values('T (K)')
            values[tag] = parsed_df['U (eV/atom)'].values

            if Tmax < parsed_df['T (K)'].values[-1]:
                Tmax = parsed_df['T (K)'].values[-1]
            
    # Add liquid
    if len(liquid_df) > 0:
        sorted_df = liquid_df.sort_values('T (K)')
        v = sorted_df['U (eV/atom)'].values
        v[~liquid_df.isliquid] = np.nan
        values['liquid'] = v

        if Tmax < sorted_df['T (K)'].values[-1]:
            Tmax = sorted_df['T (K)'].values[-1]
    
    # Build table
    table_df = build_table(values, Tmax, uc_unit)
    
    # Loop over results
    for i, tag in enumerate(values.keys()):
                
        lineformat = lineformats.iloc[i]

        # Define plot lines
        fig.add_trace(
            go.Scatter(
                x=table_df.temperature,
                y=table_df[tag],
                mode='lines',
                name=tag,
                showlegend=True,
                line=dict(
                    color=lineformat.color,
                    dash=lineformat.line)))
            
    fig.update_layout(
        title=dict(
            text="Energy vs. Temperature",
            font=dict(size=14),
        ),
        xaxis=dict(
            title=dict(
                text="Temperature (K)"
            )
        ),
        yaxis=dict(
            title=dict(
                text=f"Energy ({plot_unit})"
            )
        ),
        paper_bgcolor='white',
        plot_bgcolor='white',
    )
    fig.update_xaxes(
        range=[0, Tmax],
        **self.plotly_axes_settings
    )
    fig.update_yaxes(
        **self.plotly_axes_settings
    )
    fig.write_image(Path(contentpath, pngfile), width=1200, height=600,) 
    fig.write_html(Path(contentpath, htmlfile), include_plotlyjs='cdn', full_html=False)
    table_df.to_csv(Path(contentpath, csvfile), index=False)

    # Collect data for web generation
    dat = {}
    dat['composition'] = composition
    dat['name'] = 'Energy'
    dat['html'] = htmlfile
    dat['png'] = pngfile
    dat['csv'] = csvfile
    data.append(dat)
            
    fig.data = []

def mdthermo_cp_plot(self,
                         solid_df,
                         liquid_df,
                         composition,
                         contentpath,
                         data,
                         uc_unit='eV',
                         plot_unit='eV/atom'):
    
    # Initialize plot and table
    fig = go.Figure()
    pngfile = f'mdthermo.{composition}.U.png'
    csvfile = f'mdthermo.{composition}.U.csv'
    htmlfile = f'mdthermo.{composition}.U.html'

    lineformats = self.plotly_line_formats

    # Loop over solid prototypes
    values = {}
    Tmax = 0
    for prototype in np.unique(solid_df.prototype):
        proto_df = solid_df[solid_df.prototype == prototype]
        for i, relaxed_crystal_key in enumerate(np.unique(proto_df.relaxed_crystal_key)):
            crystal_df = proto_df[proto_df.relaxed_crystal_key == relaxed_crystal_key]
            if i == 0:
                tag = prototype
            else:
                tag = f'{prototype} ({i+1})'

            parsed_df = crystal_df[crystal_df.untransformed].sort_values('T (K)')
            values[tag] = parsed_df['U (eV/atom)'].values

            if Tmax < parsed_df['T (K)'].values[-1]:
                Tmax = parsed_df['T (K)'].values[-1]
            
    # Add liquid
    if len(liquid_df) > 0:
        sorted_df = liquid_df.sort_values('T (K)')
        v = sorted_df['U (eV/atom)'].values
        v[~liquid_df.isliquid] = np.nan
        values['liquid'] = v

        if Tmax < sorted_df['T (K)'].values[-1]:
            Tmax = sorted_df['T (K)'].values[-1]
    
    # Build table
    table_df = build_table(values, Tmax, uc_unit)
    
    # Loop over results
    for i, tag in enumerate(values.keys()):
                
        lineformat = lineformats.iloc[i]

        # Define plot lines
        fig.add_trace(
            go.Scatter(
                x=table_df.temperature,
                y=table_df[tag],
                mode='lines',
                name=tag,
                showlegend=True,
                line=dict(
                    color=lineformat.color,
                    dash=lineformat.line)))
            
    fig.update_layout(
        title=dict(
            text="Energy vs. Temperature",
            font=dict(size=14),
        ),
        xaxis=dict(
            title=dict(
                text="Temperature (K)"
            )
        ),
        yaxis=dict(
            title=dict(
                text=f"Energy ({plot_unit})"
            )
        ),
        paper_bgcolor='white',
        plot_bgcolor='white',
    )
    fig.update_xaxes(
        range=[0, Tmax],
        **self.plotly_axes_settings
    )
    fig.update_yaxes(
        **self.plotly_axes_settings
    )
    fig.write_image(Path(contentpath, pngfile), width=1200, height=600,) 
    fig.write_html(Path(contentpath, htmlfile), include_plotlyjs='cdn', full_html=False)
    table_df.to_csv(Path(contentpath, csvfile), index=False)

    # Collect data for web generation
    dat = {}
    dat['composition'] = composition
    dat['name'] = 'Energy'
    dat['html'] = htmlfile
    dat['png'] = pngfile
    dat['csv'] = csvfile
    data.append(dat)
            
    fig.data = []

def mdthermo_volume_plot(self,
                         solid_df,
                         liquid_df,
                         composition,
                         contentpath,
                         data,
                         uc_unit='eV',
                         plot_unit='eV/atom'):
    
    # Initialize plot and table
    fig = go.Figure()
    pngfile = f'mdthermo.{composition}.U.png'
    csvfile = f'mdthermo.{composition}.U.csv'
    htmlfile = f'mdthermo.{composition}.U.html'

    lineformats = self.plotly_line_formats

    # Loop over solid prototypes
    values = {}
    Tmax = 0
    for prototype in np.unique(solid_df.prototype):
        proto_df = solid_df[solid_df.prototype == prototype]
        for i, relaxed_crystal_key in enumerate(np.unique(proto_df.relaxed_crystal_key)):
            crystal_df = proto_df[proto_df.relaxed_crystal_key == relaxed_crystal_key]
            if i == 0:
                tag = prototype
            else:
                tag = f'{prototype} ({i+1})'

            parsed_df = crystal_df[crystal_df.untransformed].sort_values('T (K)')
            values[tag] = parsed_df['U (eV/atom)'].values

            if Tmax < parsed_df['T (K)'].values[-1]:
                Tmax = parsed_df['T (K)'].values[-1]
            
    # Add liquid
    if len(liquid_df) > 0:
        sorted_df = liquid_df.sort_values('T (K)')
        v = sorted_df['U (eV/atom)'].values
        v[~liquid_df.isliquid] = np.nan
        values['liquid'] = v

        if Tmax < sorted_df['T (K)'].values[-1]:
            Tmax = sorted_df['T (K)'].values[-1]
    
    # Build table
    table_df = build_table(values, Tmax, uc_unit)
    
    # Loop over results
    for i, tag in enumerate(values.keys()):
                
        lineformat = lineformats.iloc[i]

        # Define plot lines
        fig.add_trace(
            go.Scatter(
                x=table_df.temperature,
                y=table_df[tag],
                mode='lines',
                name=tag,
                showlegend=True,
                line=dict(
                    color=lineformat.color,
                    dash=lineformat.line)))
            
    fig.update_layout(
        title=dict(
            text="Energy vs. Temperature",
            font=dict(size=14),
        ),
        xaxis=dict(
            title=dict(
                text="Temperature (K)"
            )
        ),
        yaxis=dict(
            title=dict(
                text=f"Energy ({plot_unit})"
            )
        ),
        paper_bgcolor='white',
        plot_bgcolor='white',
    )
    fig.update_xaxes(
        range=[0, Tmax],
        **self.plotly_axes_settings
    )
    fig.update_yaxes(
        **self.plotly_axes_settings
    )
    fig.write_image(Path(contentpath, pngfile), width=1200, height=600,) 
    fig.write_html(Path(contentpath, htmlfile), include_plotlyjs='cdn', full_html=False)
    table_df.to_csv(Path(contentpath, csvfile), index=False)

    # Collect data for web generation
    dat = {}
    dat['composition'] = composition
    dat['name'] = 'Energy'
    dat['html'] = htmlfile
    dat['png'] = pngfile
    dat['csv'] = csvfile
    data.append(dat)
            
    fig.data = []


def build_table(values, Tmax, uc_unit):

    Tvalues = np.arange(0, Tmax+50, 50)
    
    # Build table
    table_df = {}
    table_df['temperature'] = Tvalues
    for tag in values:
        table_df[tag] = np.full_like(Tvalues, np.nan)
        table_df[tag][:len(values[tag])] = uc.get_in_units(values[tag], uc_unit)
    table_df = pd.DataFrame(table_df)

    return table_df