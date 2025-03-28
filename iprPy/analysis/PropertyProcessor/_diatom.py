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

# Local imports
from ... import load_record

def diatom(self,
           upload: bool = True,
           runall: bool = False):
    """
    Main function for processing diatom_scan calculations as used for building
    the content hosted on the NIST Interatomic Potentials Repository.
    
    Processing steps:
    
    1. diatom_scan records are retrieved from the database.
    2. Tables of data and Bokeh plots are constructed for each potential
       implementation.
    3. Flag added to PotentialProperties records to indicate plots exist.
    
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

    # Get finished records
    records_df = database.get_records_df(style='calculation_diatom_scan',
                                         status='finished', **getkwargs)

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
        if prop.diatom.exists and runall is False:
            print('skipped')
            num_skipped += 1
            continue
        
        # Build contentpath and check if it exists
        contentpath = Path(outputpath, pot_id, imp_id)
        if not contentpath.is_dir():
            contentpath.mkdir(parents=True)
        
        # Build and save table
        self.diatom_table(imp_df, outputpath, pot_id, imp_id)
        
        # Build and save main diatom plot as html and png
        self.diatom_plotly_plot(imp_df, outputpath, pot_id, imp_id)
            
        # Build and save shortrange diatom plot as html and png
        self.diatom_plotly_short_plot(imp_df, outputpath, pot_id, imp_id)
        
        # Build model component
        prop.diatom.exists = True
        model = prop.model['per-potential-properties']
        prop.diatom.build_model(model)

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

def diatom_table(self, 
                 df: pd.DataFrame,
                 outputpath: Path,
                 potential: str,
                 implementation: str):
    """
    Generates table of values for the selected content
    
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
    """

    table = '\n'.join(['# Diatom energy (eV) vs. radial distance (Angstrom).',
                       f'# potential = {potential}',
                       f'# implementation = {implementation}',
                       '# NOTE: These values only provide a look at the purely pair interaction',
                       '# of the potential and therefore exclude multi-body interactions.',
                       '',
                       '# Calculations from the NIST Interatomic Potential Repository Project:',
                       '# http://www.ctcms.nist.gov/potentials/',
                       '',
                       f'# Table generated {date.today()}'])
    
    table += '\n\nr    '
    for series in df.itertuples():
        table += '%-16s ' % series.symbols
    table += '\n'
    
    rvalues = np.array(df.iloc[0].r_values)
    for i in range(len(rvalues)):
        table += '%-4.2f ' % rvalues[i]
        for j in df.index:
            series = df.loc[j]
            table += '% -16.9e ' % series.energy_values[i]
        table += '\n'
    
    tablepath = Path(outputpath, potential, implementation, f'diatom.txt')
    with open(tablepath, 'w', encoding='UTF-8') as f:
        f.write(table)

def diatom_plotly_plot(self, 
                       df: pd.DataFrame,
                       outputpath: Path,
                       potential: str,
                       implementation: str):
    """
    Generates a Plotly plot from the data
    
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
    """
    contentpath = Path(outputpath, potential, implementation)
    if not contentpath.exists():
        contentpath.mkdir(parents=True)
    
    lineformats = self.plotly_line_formats
    
    # Initialize plot
    fig = go.Figure()
    pngfile = f'diatom.png'
    htmlfile = f'diatom.html'
    
    # Get r values
    allrvalues = np.array(df.iloc[0].r_values)
    rvalues = allrvalues[allrvalues >= 1]
    
    # Loop over energies
    lowylim = -1
    for i, index in enumerate(df.sort_values('symbols').index):
        
        lineformat = lineformats.iloc[i]
        
        series = df.loc[index]
        Evalues = np.array(series.energy_values)[allrvalues >= 1]
        
        if not np.all(np.isnan(Evalues)):
            
            # Find lowylim
            lowy = floor(np.nanmin(Evalues))
            if lowy < lowylim:
                lowylim = lowy
        
            # Define plot line
            fig.add_trace(go.Scatter(x=rvalues, y=Evalues,
                                     mode='lines',
                                     name=series.symbols,
                                     showlegend=True,
                                     line=dict(
                                         color=lineformat.color,
                                         dash=lineformat.line)
                                    )
                         )
            
    # Adjust lower y limit
    if lowylim < -20:
        lowylim = -20
        
        
    # Edit the layout
    fig.update_layout(
        title=dict(
            text=f'Diatom Energy vs. Interatomic Spacing for {implementation}',
            font=dict(size=12),
        ),
        xaxis=dict(
            title=dict(
                text='r (Angstrom)'
            )
        ),
        yaxis=dict(
            title=dict(
                text='Energy (eV)'
            )
        ),
        paper_bgcolor='white',
        plot_bgcolor='white',
    )
    fig.update_xaxes(
        range=[1, 6],
        **self.plotly_axes_settings
    )
    fig.update_yaxes(
        range=[lowylim, 1],
        **self.plotly_axes_settings
    )
    
    fig.write_image(Path(contentpath, pngfile), width=800, height=600) 
    fig.write_html(Path(contentpath, htmlfile), include_plotlyjs='cdn', full_html=False)
    fig.data = []

def diatom_plotly_short_plot(self,
                             df: pd.DataFrame,
                             outputpath: Path,
                             potential: str,
                             implementation: str):
    """
    Generates a Plotly plot from the data
    
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
    """
    contentpath = Path(outputpath, potential, implementation)
    if not contentpath.exists():
        contentpath.mkdir(parents=True)
    
    lineformats = self.plotly_line_formats
    
    # Initialize plot
    fig = go.Figure()
    pngfile = 'diatom_short.png'
    htmlfile = 'diatom_short.html'
    
    # Get r values
    rvalues = np.array(df.iloc[0].r_values)
    
    # Loop over energies
    lowylim = 0
    highylim = 0
    for i, index in enumerate(df.sort_values('symbols').index):
        
        lineformat = lineformats.iloc[i]
        
        series = df.loc[index]
        Evalues = np.array(series.energy_values)
        with np.errstate(invalid='ignore'):
            Evalues[Evalues > 1e5] = 1e5
            Evalues[Evalues < -1e5] = np.nan
        
        if not np.all(np.isnan(Evalues)):
            
            # Find lowylim
            lowy = floor(np.nanmin(Evalues))
            if lowy < lowylim:
                lowylim = lowy
        
            # Find highy based on values less than 1e5
            with np.errstate(invalid='ignore'):
                max = np.nanmax(Evalues[Evalues < 1e5])
        
            # Round up smartly
            if max > 10:
                exp = floor(np.log10(max))
                highy = int(ceil(2 * max / 10**exp) * 10**exp / 2)
            else:
                highy = ceil(max)
            if highy > highylim:
                highylim = highy
        
            # Define plot line
            fig.add_trace(go.Scatter(x=rvalues, y=Evalues,
                                     mode='lines',
                                     name=series.symbols,
                                     showlegend=True,
                                     line=dict(
                                         color=lineformat.color,
                                         dash=lineformat.line)
                                    )
                         )
            
    # Set y limits
    if lowylim < -1e5:
        lowylim = -1e5
    if highylim > 1e5:
        highylim = 1e5
        
    # Edit the layout
    fig.update_layout(
        title=dict(
            text=f'Diatom Energy vs. Interatomic Spacing for {implementation}',
            font=dict(size=12),
        ),
        xaxis=dict(
            title=dict(
                text='r (Angstrom)'
            )
        ),
        yaxis=dict(
            title=dict(
                text='Energy (eV)'
            )
        ),
        paper_bgcolor='white',
        plot_bgcolor='white',
    )
    fig.update_xaxes(
        range=[0, 2],
        **self.plotly_axes_settings
    )
    fig.update_yaxes(
        range=[lowylim, highylim],
        **self.plotly_axes_settings
    )
    
    fig.write_image(Path(contentpath, pngfile), width=800, height=600) 
    fig.write_html(Path(contentpath, htmlfile), include_plotlyjs='cdn', full_html=False)
    fig.data = []