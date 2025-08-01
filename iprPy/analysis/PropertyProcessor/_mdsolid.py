# coding: utf-8

# Standard Python libraries
from pathlib import Path
from datetime import date
from math import floor, ceil

# http://www.numpy.org/
import numpy as np

# https://pandas.pydata.org/
import pandas as pd

# https://plotly.com/python
import plotly.graph_objects as go

from atomman import Box, ElasticConstants2

# Local imports
from ... import load_record



def mdsolid(self,
           upload: bool = True,
           runall: bool = False):
    """
    Main function for processing the structural results in md_solid_properties
    records as used for building the content hosted on the NIST Interatomic
    Potentials Repository.
    
    Processing steps:
    
    1. md_solid_properties records are retrieved from the database.
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
    getkwargs = self.getkwargs
    outputpath = self.outputpath
    props = self.props
    prop_df = self.prop_df()

    # Get records
    records_df = database.get_records_df(style='md_solid_properties',
                                         **getkwargs)
    
    # Add prototype field
    self.identify_prototypes(records_df)

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
        if prop.mdsolid.exists and runall is False:
            print('skipped')
            num_skipped += 1
            continue
        
        # Loop over relaxed_crystal_keys sorted by composition and family
        sort_keys = ['composition', 'family', 'relaxed_crystal_key']
        for relaxed_crystal_key in imp_df.sort_values(sort_keys).relaxed_crystal_key.unique():
            crystal_df = imp_df[imp_df.relaxed_crystal_key == relaxed_crystal_key]
            composition = crystal_df.composition.values[0]
            family = crystal_df.family.values[0]
            alat = crystal_df.a.values[0]
            tag = f'mdsolid.{composition}.{family}.{relaxed_crystal_key[:8]}'

            # Process and save the structure data
            processed_df = self.mdsolid_table(crystal_df, outputpath, pot_id, imp_id, tag)

            # Build and save alat and cij plots as html and png
            self.mdsolid_alat_plotly_plot(processed_df, outputpath, pot_id, imp_id, tag)
            self.mdsolid_cij_plotly_plot(processed_df, outputpath, pot_id, imp_id, tag)
            
        # Build model component
        prop.mdsolid.exists = True
        model = prop.model['per-potential-properties']
        prop.mdsolid.build_model(model)

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

def mdsolid_table(self,
                  df: pd.DataFrame,
                  outputpath: Path,
                  potential: str,
                  implementation: str,
                  tag: str) -> pd.DataFrame:
    """
    Processes and extracts structural information
    
    Parameters
    ----------
    df : pandas.DataFrame
        The records_df for md_solid_properties records associated with a single
        ancestor relaxed_crystal_key.
    outputpath : pathlib.Path
        The root location where all generated web content files are saved.
    potential : str
        Name of the potential model associated with the records.
    implementation : str
        Name of the potential implementation associated with the records.
    tag : str
        The core file name to use for the md solid structure tables and figures.

    Returns
    -------
    processed_df : pandas.DataFrame
        A new dataframe containing only cleaned up structural information.
    """
    contentpath = Path(outputpath, potential, implementation)
    if not contentpath.exists():
        contentpath.mkdir(parents=True)
    csvfile = f'{tag}.csv'

    # Filter out transformed results
    parsed_df = df[df.untransformed]

    # Sort values by temperature
    sorted_df = parsed_df.sort_values('T (K)')

    # Identify the crystal symmetry family of the 0K structure
    series = sorted_df.iloc[0]
    box = Box(a=series.a, b=series.b, c=series.c, alpha=series.alpha, beta=series.beta, gamma=series.gamma)
    symmetryfamily = box.identifyfamily()

    processed_df = []
    for index in sorted_df.index:
        series = sorted_df.loc[index]

        # Copy temperature and lattice constants over
        data = {}
        data['temperature'] = series['T (K)']
        data['a'] = series['a']
        data['b'] = series['b']
        data['c'] = series['c']
        data['alpha'] = series['alpha']
        data['beta'] = series['beta']
        data['gamma'] = series['gamma']

        # Build elastic constants object
        cdict = {}
        for key in sorted_df.keys():
            if key[0] == 'C':
                cdict[key[:3]] = series[key]
        C = ElasticConstants2(**cdict)

        # Normalize elastic constants and add only unique values to data
        data.update(C.normalized_as(symmetryfamily, return_dict=True))

        processed_df.append(data)
    
    processed_df = pd.DataFrame(processed_df)

    # Save and return processed_df
    processed_df.to_csv(Path(contentpath, csvfile), index=False)

    return processed_df

def mdsolid_alat_plotly_plot(self, 
                             df: pd.DataFrame,
                             outputpath: Path,
                             potential: str,
                             implementation: str,
                             tag: str):
    """
    Generates a Plotly plot from the lattice constant data
    
    Parameters
    ----------
    df : pandas.DataFrame
        The records_df for calculation_diatom_scan records to include.
    outputpath : pathlib.Path
        The root location where all generated web content files are saved.
    potential : str
        Name of the potential model associated with the records.
    implementation : str
        Name of the potential implementation associated with the records.
    tag : str
        The core file name to use for the md solid structure tables and figures.
    """
    contentpath = Path(outputpath, potential, implementation)
    if not contentpath.exists():
        contentpath.mkdir(parents=True)
    
    lineformats = self.plotly_line_formats
    
    # Initialize plot
    fig = go.Figure()
    pngfile = f'{tag}.a.png'
    htmlfile = f'{tag}.a.html'
    
    # Loop over alat keys
    for i, key in enumerate(['a', 'b', 'c']):

        lineformat = lineformats.iloc[i]

        # Define plot lines
        fig.add_trace(
            go.Scatter(
                x=df.temperature,
                y=df[key],
                mode='lines',
                name=key,
                showlegend=True,
                line=dict(
                    color=lineformat.color,
                    dash=lineformat.line)))
        
    # Edit the layout
    fig.update_layout(
        title=dict(
            text=f'Lattice constants vs. Temperature',
            font=dict(size=12),
        ),
        xaxis=dict(
            title=dict(
                text='Temperature (K)'
            )
        ),
        yaxis=dict(
            title=dict(
                text='Lattice constant (Angstrom)'
            )
        ),
        paper_bgcolor='white',
        plot_bgcolor='white',
    )
    Tmax = df.temperature.values[-1]
    if Tmax == 0:
        Tmax = 50
    fig.update_xaxes(
        range=[0, Tmax],
        **self.plotly_axes_settings
    )
    fig.update_yaxes(
        **self.plotly_axes_settings
    )
    
    fig.write_image(Path(contentpath, pngfile), width=800, height=600) 
    fig.write_html(Path(contentpath, htmlfile), include_plotlyjs='cdn', full_html=False)
    fig.data = []

def mdsolid_cij_plotly_plot(self,
                             df: pd.DataFrame,
                             outputpath: Path,
                             potential: str,
                             implementation: str,
                             tag: str):
    """
    Generates a Plotly plot from the elastic constant data
    
    Parameters
    ----------
    df : pandas.DataFrame
        The records_df for calculation_diatom_scan records to include.
    outputpath : pathlib.Path
        The root location where all generated web content files are saved.
    potential : str
        Name of the potential model associated with the records.
    implementation : str
        Name of the potential implementation associated with the records.
    tag : str
        The core file name to use for the md solid structure tables and figures.
    """
    contentpath = Path(outputpath, potential, implementation)
    if not contentpath.exists():
        contentpath.mkdir(parents=True)
    
    lineformats = self.plotly_line_formats
    
    # Initialize plot
    fig = go.Figure()
    pngfile = f'{tag}.Cij.png'
    htmlfile = f'{tag}.Cij.html'
    
    # Identify Cij keys
    Cijkeys = []
    for key in df.keys():
        if key[0] == 'C':
            Cijkeys.append(key)

    # Loop over Cij keys
    for i, key in enumerate(Cijkeys):
        
        lineformat = lineformats.iloc[i]
        
        # Define plot lines
        fig.add_trace(
            go.Scatter(
                x=df.temperature,
                y=df[key],
                mode='lines',
                name=key,
                showlegend=True,
                line=dict(
                    color=lineformat.color,
                    dash=lineformat.line)))
        
    # Edit the layout
    fig.update_layout(
        title=dict(
            text=f'Elastic Constants vs. Temperature',
            font=dict(size=12),
        ),
        xaxis=dict(
            title=dict(
                text='Temperature (K)'
            )
        ),
        yaxis=dict(
            title=dict(
                text='Cij (GPa)'
            )
        ),
        paper_bgcolor='white',
        plot_bgcolor='white',
    )
    Tmax = df.temperature.values[-1]
    if Tmax == 0:
        Tmax = 50
    fig.update_xaxes(
        range=[0, Tmax],
        **self.plotly_axes_settings
    )
    fig.update_yaxes(
        **self.plotly_axes_settings
    )
    
    fig.write_image(Path(contentpath, pngfile), width=800, height=600) 
    fig.write_html(Path(contentpath, htmlfile), include_plotlyjs='cdn', full_html=False)
    fig.data = []