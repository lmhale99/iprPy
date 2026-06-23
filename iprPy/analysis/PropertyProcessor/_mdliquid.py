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

import dbliquid
from atomman import Box, ElasticConstants2

# Local imports
from ... import load_record



def mdliquid(self,
           upload: bool = True,
           runall: bool = False):
    """
    Main function for processing the structural results in md_liquid_properties
    records as used for building the content hosted on the NIST Interatomic
    Potentials Repository.
    
    Processing steps:
    
    1. md_liquid_properties records are retrieved from the database.
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
    outputpath = self.outputpath

    num_updated = 0
    num_skipped = 0
    for prop, getkwargs in self.iter_by_prop():
        pot_id = prop.potential_id
        imp_id = prop.potential_LAMMPS_id

        # Skip records with existing results
        if prop.mdliquid.exists and runall is False:
            print('skipped')
            num_skipped += 1
            continue
        else:
            # reset data
            prop.mdliquid.compositions.clear()
        
        # Get records
        imp_df = database.get_records_df(style='md_liquid_properties',
                                             **getkwargs)
        if len(imp_df) > 0:
            imp_df = imp_df[np.isclose(imp_df['P (MPa)'], 0.0)]
        if len(imp_df) == 0:
            print('no finished records')
            continue

        # Add keys if needed
        for key in ['D MSD full (m^2/s)', 'D MSD mean (m^2/s)', 'μ GK (Pa*s)']:
            if key not in imp_df:
                imp_df[key] = np.nan

        # Loop over compositions
        for composition in np.unique(imp_df.composition):
            liquid_df = imp_df[imp_df.composition == composition]
            tag = f'mdliquid.{composition}'

            # Process and save the structure data
            processed_df = self.mdliquid_table(liquid_df, outputpath, pot_id, imp_id, tag)
            if len(processed_df) == 0:
                continue

            # Build and save alat and cij plots as html and png
            self.mdliquid_diffusion_plot(processed_df, outputpath, pot_id, imp_id, tag)
            self.mdliquid_viscosity_plot(processed_df, outputpath, pot_id, imp_id, tag)
            
            # Get RDFs and build plots
            self.mdliquid_rdf_plot(liquid_df, database, outputpath, pot_id, imp_id, tag)

            # Add composition listing to PotentialProperties content
            prop.mdliquid.compositions.append(composition)

        # Build model component
        prop.mdliquid.exists = True
        model = prop.model['per-potential-properties']
        prop.mdliquid.build_model(model)

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

def mdliquid_table(self,
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
        The records_df for md_liquid_properties records associated with a single
        composition.
    outputpath : pathlib.Path
        The root location where all generated web content files are saved.
    potential : str
        Name of the potential model associated with the records.
    implementation : str
        Name of the potential implementation associated with the records.
    tag : str
        The core file name to use for the md liquid tables and figures.

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
    parsed_df = df[df.isliquid]

    # Sort values by temperature
    sorted_df = parsed_df.sort_values('T (K)')


    include_keys = ['T (K)', 'D MSD full (m^2/s)', 'D MSD mean (m^2/s)', 'μ GK (Pa*s)']
    processed_df = sorted_df[include_keys]


    # Save and return processed_df
    if len(processed_df) > 1:
        processed_df.to_csv(Path(contentpath, csvfile), index=False)

    return processed_df

def mdliquid_diffusion_plot(self, 
                            df: pd.DataFrame,
                            outputpath: Path,
                            potential: str,
                            implementation: str,
                            tag: str):
    """
    Generates a Plotly plot from the diffusion data
    
    Parameters
    ----------
    df : pandas.DataFrame
        The records_df for md_liquid_properties records to include.
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
    pngfile = f'{tag}.D.png'
    htmlfile = f'{tag}.D.html'
    
    # Loop over alat keys
    for i, key in enumerate(['D MSD full (m^2/s)', 'D MSD mean (m^2/s)']):

        lineformat = lineformats.iloc[i]

        # Define plot lines
        fig.add_trace(
            go.Scatter(
                x=df['T (K)'],
                y=df[key],
                mode='markers',
                name=key,
                showlegend=True,
                marker=dict(
                    color=lineformat.color)))
        
    # Edit the layout
    fig.update_layout(
        title=dict(
            text=f'Diffusion constants vs. Temperature',
            font=dict(size=12),
        ),
        xaxis=dict(
            title=dict(
                text='Temperature (K)'
            )
        ),
        yaxis=dict(
            title=dict(
                text='Diffusion constant (m^2/s)'
            )
        ),
        paper_bgcolor='white',
        plot_bgcolor='white',
    )
    Tmax = df['T (K)'].values[-1]
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

def mdliquid_viscosity_plot(self,
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
    pngfile = f'{tag}.mu.png'
    htmlfile = f'{tag}.mu.html'
        
    lineformat = lineformats.iloc[0]
    
    # Define plot lines
    fig.add_trace(
        go.Scatter(
            x=df['T (K)'],
            y=df['μ GK (Pa*s)'],
            mode='markers',
            marker=dict(
                color=lineformat.color)))
        
    # Edit the layout
    fig.update_layout(
        title=dict(
            text=f'Viscosity vs. Temperature',
            font=dict(size=12),
        ),
        xaxis=dict(
            title=dict(
                text='Temperature (K)'
            )
        ),
        yaxis=dict(
            title=dict(
                text='&#956; GK (Pa*s)'
            )
        ),
        paper_bgcolor='white',
        plot_bgcolor='white',
    )
    Tmax = df['T (K)'].values[-1]
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


def mdliquid_rdf_plot(self,
                      df: pd.DataFrame,
                      database,
                      outputpath: Path,
                      potential: str,
                      implementation: str,
                      tag: str):
    """
    Generates a Plotly plot from the liquid RDF curves
    
    Parameters
    ----------
    df : pandas.DataFrame
        The records_df for md_liquid_results records that correspond to the RDF
        records to find and include.
    database : iprPy.Database
        The database to fetch the RDF records from.
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
    
    # Sort and filter df
    parsed_df = df[df.isliquid].sort_values('T (K)')

    # Fetch corresponding rdf records
    rdfs, rdfs_df = database.get_records('rdf', relax_liquid_key=parsed_df.relax_liquid_key.tolist(), return_df=True)

    # Initialize plot
    fig = go.Figure()
    pngfile = f'{tag}.rdf.png'
    htmlfile = f'{tag}.rdf.html'

    rmax = 0
    for i, index in enumerate(rdfs_df.sort_values('T (K)').index):
        rdf = rdfs[index]

        lineformat = lineformats.iloc[i]
        
        # Define plot lines
        fig.add_trace(
            go.Scatter(
                x=rdf.r,
                y=rdf.g,
                mode='lines',
                name=rdf.temperature,
                showlegend=True,
                line=dict(
                    color=lineformat.color,
                    dash=lineformat.line)))
        if rdf.r[-1] > rmax:
            rmax = rdf.r[-1]
        
    # Edit the layout
    fig.update_layout(
        title=dict(
            text=f'Radial Distribution Function',
            font=dict(size=12),
        ),
        xaxis=dict(
            title=dict(
                text='r (Angstrom)'
            )
        ),
        yaxis=dict(
            title=dict(
                text='g(r)'
            )
        ),
        paper_bgcolor='white',
        plot_bgcolor='white',
    )

    fig.update_xaxes(
        range=[0, rmax],
        **self.plotly_axes_settings
    )
    fig.update_yaxes(
        range=[0, None],
        **self.plotly_axes_settings
    )
    
    fig.write_image(Path(contentpath, pngfile), width=800, height=600) 
    fig.write_html(Path(contentpath, htmlfile), include_plotlyjs='cdn', full_html=False)
    fig.data = []