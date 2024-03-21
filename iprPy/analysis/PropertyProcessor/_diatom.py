# coding: utf-8

# Standard Python libraries
from pathlib import Path
from datetime import date
from math import floor, ceil

# http://www.numpy.org/
import numpy as np

# https://pandas.pydata.org/
import pandas as pd

# https://docs.bokeh.org/en/latest/
import bokeh

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
        diatom_table(imp_df, outputpath, pot_id, imp_id)
        
        # Build and save main diatom plot as html and png
        diatom_bokeh_plot(imp_df, outputpath, pot_id, imp_id)
            
        # Build and save shortrange diatom plot as html and png
        diatom_bokeh_short_plot(imp_df, outputpath, pot_id, imp_id)
        
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

def diatom_table(df: pd.DataFrame,
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
    
def get_lineformats() -> pd.DataFrame:
    """
    Defines the line colors and styles to use for each plotted family.
    """
    lineformats = []
    colors = ['black', 'blue', 'red', 'cyan', 'magenta', '#EAC117', 'orange', 'gray', 'green','brown']
    lines = ['solid', 'dashed', 'dotted', 'dashdot', 'solid', 'dashed', 'dotted', 'dashdot']
    
    for line in lines:
        for color in colors:
            lineformats.append({'color':color, 'line':line})
    
    return pd.DataFrame(lineformats)

def diatom_bokeh_plot(df: pd.DataFrame,
                      outputpath: Path,
                      potential: str,
                      implementation: str):
    """
    Generates a Bokeh plot from the data
    
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
    resources = bokeh.resources.Resources(mode='cdn')

    lineformats = get_lineformats()
    
    # Initialize plot
    title = f'Diatom Energy vs. Interatomic Spacing for {implementation}'
    p = bokeh.plotting.figure(title = title,
                              width = 800,
                              height = 600,
                              x_range = [1, 6],
                              y_range = [-20, 1],
                              x_axis_label = 'r (Angstrom)', 
                              y_axis_label = 'Energy (eV)')
    
    # Get r values
    rvalues = np.array(df.iloc[0].r_values)
    
    # Loop over energies
    lowylim = -1
    for i, series in enumerate(df.itertuples()):
        Evalues = np.array(series.energy_values)
        Evalues[rvalues < 1] = np.nan
        
        lineformat = lineformats.iloc[i]
        
        if not np.all(np.isnan(Evalues)):
            
            # Find lowylim
            lowy = floor(np.nanmin(Evalues))
            if lowy < lowylim:
                lowylim = lowy
        
            # Define plot line
            l = p.line(rvalues, Evalues, legend_label=series.symbols, 
                       line_color=lineformat.color, line_dash=lineformat.line, line_width = 2)
            p.add_tools(bokeh.models.HoverTool(renderers=[l],
                                               tooltips=[("symbols", series.symbols),
                                                         ("r (Angstrom)", "$x"),
                                                         ("energy (eV)", "$y")]))
    # Adjust lower y limit
    if lowylim < -20:
        lowylim = -20
    p.y_range = bokeh.models.Range1d(lowylim, 1)
    
    # Set legend location
    p.legend.location = "bottom_right"
    
    htmlpath = Path(outputpath, potential, implementation, f'diatom.html')
    
    bokeh.io.save(p, htmlpath, resources=resources, 
                  title='Interatomic Potentials Repository Project')
    
    pngpath = Path(outputpath, potential, implementation, f'diatom.png')
    bokeh.io.export_png(p, filename=pngpath)
    bokeh.io.reset_output() 

def diatom_bokeh_short_plot(df: pd.DataFrame,
                            outputpath: Path,
                            potential: str,
                            implementation: str):
    """
    Generates a Bokeh plot from the data
    
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
    resources = bokeh.resources.Resources(mode='cdn')

    lineformats = get_lineformats()
    
    # Initialize plot
    title = f'Diatom Energy vs. Interatomic Spacing for {implementation}'
    p = bokeh.plotting.figure(title = title,
                              width = 800,
                              height = 600,
                              x_range = [0, 2],
                              y_range = [-5e5, 5e5],
                              x_axis_label = 'r (Angstrom)', 
                              y_axis_label = 'Energy (eV)')
    
    # Get r values
    rvalues = np.array(df.iloc[0].r_values)
    
    # Loop over energies
    lowylim = 0
    highylim = 0
    for i, series in enumerate(df.itertuples()):
        Evalues = np.array(series.energy_values)
        with np.errstate(invalid='ignore'):
            Evalues[Evalues > 1e5] = 1e5
            Evalues[Evalues < -1e5] = np.nan
        
        lineformat = lineformats.iloc[i]
        
        if not np.all(np.isnan(Evalues)):
            
            # Find ylims
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
            l = p.line(rvalues, Evalues, legend_label=series.symbols, 
                       line_color=lineformat.color, line_dash=lineformat.line, line_width = 2)
            p.add_tools(bokeh.models.HoverTool(renderers=[l],
                                               tooltips=[("symbols", series.symbols),
                                                         ("r (Angstrom)", "$x"),
                                                         ("energy (eV)", "$y")]))
    # Set y limits
    if lowylim < -1e5:
        lowylim = -1e5
    if highylim > 1e5:
        highylim = 1e5
    p.y_range = bokeh.models.Range1d(lowylim, highylim)
    
    # Set legend location
    p.legend.location = "bottom_right"
    
    htmlpath = Path(outputpath, potential, implementation, f'diatom_short.html')
    bokeh.io.save(p, htmlpath, resources=resources, 
                  title = 'Interatomic Potentials Repository Project')
    
    pngpath = Path(outputpath, potential, implementation, f'diatom_short.png')
    bokeh.io.export_png(p, filename=pngpath)
    bokeh.io.reset_output()