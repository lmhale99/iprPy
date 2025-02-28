# coding: utf-8

# Standard Python libraries
from pathlib import Path
from datetime import date
from math import floor

# http://www.numpy.org/
import numpy as np

# https://pandas.pydata.org/
import pandas as pd

# https://plotly.com/python
import plotly.graph_objects as go

# Local imports
from ... import load_record

def evsr(self, 
         upload: bool = True,
         runall: bool = False):
    """
    Main function for processing E_vs_r_scan calculations as used for building
    the content hosted on the NIST Interatomic Potentials Repository.
    
    Processing steps:
    
    1. calculation_E_vs_r_scan records are retrieved from the database.
    2. Tables of data and Bokeh plots are constructed for each unique potential
       implementation and composition.
    3. Listings of generated plots are added to PotentialProperties records.
    
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
    records_df = database.get_records_df(style='calculation_E_vs_r_scan',
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
        if prop.evsr.exists and runall is False:
            print('skipped')
            num_skipped += 1
            continue
        else:
            # reset data
            prop.evsr.compositions.clear()
        
        # Build contentpath and check if it exists
        contentpath = Path(outputpath, pot_id, imp_id)
        if not contentpath.is_dir():
            contentpath.mkdir(parents=True)
        
        # Loop over compositions
        for composition in np.unique(imp_df.composition):
            comp_df = imp_df[imp_df.composition == composition].sort_values('family')
            
            # Build and save table
            self.evsr_table(comp_df, outputpath, pot_id, imp_id, composition)
            
            # Build and save EvsR plot as html and png
            self.evsr_plotly_plot(comp_df, outputpath, pot_id, imp_id, composition)
            
            # Add composition listing to PotentialProperties content
            prop.evsr.compositions.append(composition)
        
        # Build model component
        prop.evsr.exists = True
        model = prop.model['per-potential-properties']
        prop.evsr.build_model(model)

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

def evsr_table(self,
               df: pd.DataFrame,
               outputpath: Path,
               potential: str,
               implementation: str,
               composition: str):
    """
    Generates table of values for the selected content
    
    Parameters
    ----------
    df : pandas.DataFrame
        The records_df for calculation_E_vs_r_scan records to include.
    outputpath : pathlib.Path
        The root location where all generated web content files are saved.
    potential : str
        Name of the potential model associated with the records.
    implementation : str
        Name of the potential implementation associated with the records.
    composition : str
        The elemental composition associated with the records.
        
    Returns
    -------
    table : str
        The generated table file contents.
    """

    table = '\n'.join(['# Potential energy (eV/atom) vs. nearest neighbor radial distance (Angstrom).',
                       f'# potential = {potential}',
                       f'# implementation = {implementation}',
                       f'# composition = {composition}',
                       '# NOTE: These values are for static, unrelaxed structures and use the ideal',
                       '# b/a and c/a ratios for the crystal structure, not the potential-specific',
                       '# values.',
                       '',
                       '# Calculations from the NIST Interatomic Potential Repository Project:',
                       '# http://www.ctcms.nist.gov/potentials/',
                       '',
                       f'# Table generated {date.today()}'])
    
    table += '\n\nr    '
    rmin = 999
    rmax = 0
    rstep = None
    for i in df.index:
        
        series = df.loc[i]
        family = series.family
        if len(family) > 16: 
            family = family[:16]
        table += '%-16s ' %family
        rvalues = np.array(series.r_values)
        if rmin > rvalues.min():
            rmin = rvalues.min()
        if rmax < rvalues.max():
            rmax = rvalues.max()
        if rstep is None:
            rstep = rvalues[1] - rvalues[0]
        elif not np.isclose(rstep, rvalues[1] - rvalues[0]):
            raise ValueError(f'Different rstep: {implementation} {composition} {family}')

    table += '\n'
    
    nsteps = round((rmax - rmin) / rstep) + 1

    for r in np.linspace(rmin, rmax, nsteps):
        table += '%-4.2f ' % r
        for i in df.index:
            series = df.loc[i]
            energy_values = np.array(series.energy_values)
            r_values = np.array(series.r_values)
            try:
                e = energy_values[np.isclose(r, r_values)][0]
            except:
                e = np.nan
            table += '% -16.9e ' % e
        table += '\n'

    tablepath = Path(outputpath, potential, implementation,
                     f'EvsR.{composition}.txt')
    with open(tablepath, 'w', encoding='UTF-8') as f:
        f.write(table)
    
def get_lineformats():
    """
    Defines the line colors and styles to use for each plotted family.
    """
    lineformats = []
    
    # Unary
    lineformats.append({'family':'A1--Cu--fcc',                'color':'black',   'line':'solid'})
    lineformats.append({'family':'A2--W--bcc',                 'color':'blue',    'line':'solid'})
    lineformats.append({'family':'A3--Mg--hcp',                'color':'red',     'line':'dash'})
    lineformats.append({'family':'A3\'--alpha-La--double-hcp', 'color':'cyan',    'line':'dashdot'})
    lineformats.append({'family':'A4--C--dc',                  'color':'magenta', 'line':'solid'})
    lineformats.append({'family':'A5--beta-Sn',                'color':'#EAC117', 'line':'solid'})
    lineformats.append({'family':'A6--In--bct',                'color':'orange',  'line':'solid'})
    lineformats.append({'family':'A7--alpha-As',               'color':'gray',    'line':'solid'})
    lineformats.append({'family':'A15--beta-W',                'color':'green',   'line':'solid'})
    lineformats.append({'family':'Ah--alpha-Po--sc',           'color':'brown',   'line':'solid'})
    
    # AB binary
    lineformats.append({'family':'B1--NaCl--rock-salt',        'color':'black',   'line':'solid'})
    lineformats.append({'family':'B2--CsCl',                   'color':'blue',    'line':'solid'})
    lineformats.append({'family':'B3--ZnS--cubic-zinc-blende', 'color':'red',     'line':'solid'})
    lineformats.append({'family':'L1_0--AuCu',                 'color':'cyan',    'line':'solid'})
    
    # AB2 binary
    lineformats.append({'family':'C1--CaF2--fluorite',         'color':'black',   'line':'solid'})
    
    # AB3 binary
    lineformats.append({'family':'A15--Cr3Si',                 'color':'black',   'line':'solid'})
    lineformats.append({'family':'D0_3--BiF3',                 'color':'blue',    'line':'solid'})
    lineformats.append({'family':'L1_2--AuCu3',                'color':'red',     'line':'solid'})
    
    # ABC2 ternary
    lineformats.append({'family':'L2_1--AlCu2Mn--heusler',     'color':'black',   'line':'solid'})
    
    return pd.DataFrame(lineformats)

def evsr_plotly_plot(self,
                     df: pd.DataFrame,
                     outputpath: Path,
                     potential: str,
                     implementation: str,
                     composition: str):
    """
    Generates a Plotly plot from the data
    
    Parameters
    ----------
    df : pandas.DataFrame
        The records_df for calculation_E_vs_r_scan records to include.
    outputpath : pathlib.Path
        The root location where all generated web content files are saved.
    potential : str
        Name of the potential model associated with the records.
    implementation : str
        Name of the potential implementation associated with the records.
    composition : str
        The elemental composition associated with the records.
    """
    contentpath = Path(outputpath, potential, implementation)
    if not contentpath.exists():
        contentpath.mkdir(parents=True)
    
    lineformats = get_lineformats()
    
    # Initialize plot
    fig = go.Figure()
    pngfile = f'EvsR.{composition}.png'
    htmlfile = f'EvsR.{composition}.html'
    
    # Loop over energies
    lowylim = -1
    for i, index in enumerate(df.sort_values('family').index):
        
        series = df.loc[index]
        family = series.family
        rvalues = np.array(series.r_values)
        Evalues = np.array(series.energy_values)
        Evalues[np.abs(np.nan_to_num(Evalues)) > 1e5] = np.nan
        
        lineformat = lineformats[lineformats.family==family].iloc[0]
        
        if not np.all(np.isnan(Evalues)):
            
            # Find lowylim
            lowy = floor(np.nanmin(Evalues))
            if lowy < lowylim:
                lowylim = lowy
        
            # Define plot line
            fig.add_trace(go.Scatter(x=rvalues, y=Evalues,
                                     mode='lines',
                                     name=family,
                                     showlegend=True,
                                     line=dict(
                                         color=lineformat.color,
                                         dash=lineformat.line)
                                    )
                         )
            
    # Adjust lower y limit
    if lowylim < -10:
        lowylim = -10
        
    # Edit the layout
    fig.update_layout(
        title=dict(
            text=f'Potential Energy vs. Interatomic Spacing for {composition} Using {implementation}',
            font=dict(size=12),
        ),
        xaxis=dict(
            title=dict(
                text='r (Angstrom)'
            )
        ),
        yaxis=dict(
            title=dict(
                text='Potential Energy (eV/atom)'
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
    
    fig.write_image(Path(contentpath, pngfile), width=1200, height=600) 
    fig.write_html(Path(contentpath, htmlfile), include_plotlyjs='cdn', full_html=False)
    fig.data = []