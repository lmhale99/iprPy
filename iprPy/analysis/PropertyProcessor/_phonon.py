# coding: utf-8

# Standard Python libraries
from pathlib import Path
from copy import deepcopy

# http://www.numpy.org/
import numpy as np

# https://pandas.pydata.org/
import pandas as pd

import plotly.graph_objects as go

import matplotlib.pyplot as plt

import atomman.unitconvert as uc

# Local imports
from ..thermo import AnalyzeQHA

def phonon(self, 
           upload: bool = True,
           runall: bool = False):
    """
    Main function for processing phonon calculations as used
    for building the content hosted on the NIST Interatomic Potentials
    Repository.
    
    Processing steps:
    
    1. calculation_phonon records are retrieved from the database.
    2. Basic plots are extracted from the record tars.
    3. Plots and csv files for thermo data are generated for each composition.
    
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

    # Load parent records
    parents_df = self.crystals_df

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
        if prop.phonons.exists and runall is False:
            print('skipped')
            num_skipped += 1
            continue

        # Get records and records_df
        records, records_df = database.get_records(style='calculation_phonon',
                                                   status='finished', return_df=True,
                                                   potential_key=pot_key,
                                                   potential_LAMMPS_key=imp_key,
                                                   **getkwargs)
        if len(records) == 0:
            print('no finished records found')
            continue    
        
        # Add prototype field
        self.identify_prototypes(records_df)

        # Merge parent data into records
        records_df = records_df.merge(parents_df, left_on='parent_key', right_on='key',
                                      suffixes=('', '_parent'), validate='many_to_one')
    
        # Build contentpath and check if it exists
        contentpath = Path(outputpath, pot_id, imp_id)
        if not contentpath.is_dir():
            contentpath.mkdir(parents=True)
        
        # Loop over records to extract files and create qha analysis objects
        qhas = []
        phononplot = []
        for record_index in records_df.index:
            record = records[record_index]
            record_series = records_df.loc[record_index]

            # Estimate natoms in primitive cell and create analysis object
            if not np.isnan(record_series.E0):
                natoms = record.dos['projected_dos'].shape[0]
                qhas.append(AnalyzeQHA(record, natoms))
            else:
                qhas.append(np.nan)

            # Extract plots from tar files
            self.phonon_extract_plots(database, record, record_series, contentpath, phononplot)
            record.clear_tar()

        # Add qha objects to the data frame
        records_df['qha'] = qhas
        
        # Loop over compositions to build thermo plots
        thermoplot = []
        for composition in np.unique(records_df.composition):
            comp_records_df = records_df[records_df.composition == composition]

            self.phonon_thermo_plots(comp_records_df, composition, contentpath, thermoplot)
        
        # Build info tables for the extracted/generated plots
        prop.phonons.phononplot = pd.DataFrame(phononplot)
        prop.phonons.thermoplot = pd.DataFrame(thermoplot)
        
        # Build model component
        prop.phonons.exists = True
        model = prop.model['per-potential-properties']
        prop.phonons.build_model(model)

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


def phonon_extract_plots(self, database, record, series, contentpath, data):
    """
    Fetch a phonon record's tar file and extract the figures contained in it.
    """
    # Get the record's tar to extract contained plot figures 
    tar = record.tar
    tarnames = tar.getnames()
    
    # Set root name for extracted files
    fileroot = f'phonon.{series.composition}.{series.family}.{series.key.split("-")[0]}'

    # Extract the band images
    fname = f'{fileroot}.band.png'
    tarname = f'{series.key}/band.png'
    if tarname in tarnames:
        ftar = tar.extractfile(tarname)
        with open(Path(contentpath, fname), 'wb') as fout:
            fout.write(ftar.read())
        ftar.close()
        dat = {}
        dat['composition'] = series.composition
        dat['prototype'] = series.prototype
        dat['a'] = series.a
        dat['name'] = 'band structure'
        dat['png'] = fname
        data.append(dat)

    # Generate DOS plot
    fname = f'{fileroot}.dos.png'
    plt.plot(uc.get_in_units(record.dos['frequency'], 'THz'), record.dos['total_dos'])
    plt.xlabel('Frequency (THz)', size='x-large')
    plt.ylabel('Density of States', size='x-large')
    plt.ylim(0, None) 
    plt.savefig(Path(contentpath, fname))
    plt.close()
    dat = {}
    dat['composition'] = series.composition
    dat['prototype'] = series.prototype
    dat['a'] = series.a
    dat['name'] = 'density of states'
    dat['png'] = fname
    data.append(dat)

    # Generate PDOS plot
    fname = f'{fileroot}.pdos.png'
    for pdos in record.dos['projected_dos']:
        plt.plot(uc.get_in_units(record.dos['frequency'], 'THz'), pdos)
    plt.xlabel('Frequency (THz)', size='x-large')
    plt.ylabel('Partial Density of States', size='x-large')
    plt.ylim(0, None)
    plt.savefig(Path(contentpath, fname))
    plt.close()
    dat = {}
    dat['composition'] = series.composition
    dat['prototype'] = series.prototype
    dat['a'] = series.a
    dat['name'] = 'partial density of states'
    dat['png'] = fname
    data.append(dat)

    # Extract the bulk modulus images
    fname = f'{fileroot}.bmod.png'
    tarname = f'{series.key}/bulk_modulus.png'
    if tarname in tarnames:
        ftar = tar.extractfile(tarname)
        with open(Path(contentpath, fname), 'wb') as fout:
            fout.write(ftar.read())
        ftar.close()
        dat = {}
        dat['composition'] = series.composition
        dat['prototype'] = series.prototype
        dat['a'] = series.a
        dat['name'] = 'bulk modulus'
        dat['png'] = fname
        data.append(dat)

    # Extract the band images
    fname = f'{fileroot}.helmvol.png'
    tarname = f'{series.key}/helmholtz_volume.png'
    if tarname in tarnames:
        ftar = tar.extractfile(tarname)
        with open(Path(contentpath, fname), 'wb') as fout:
            fout.write(ftar.read())
        ftar.close()
        dat = {}
        dat['composition'] = series.composition
        dat['prototype'] = series.prototype
        dat['a'] = series.a
        dat['name'] = 'Helmholtz vs. volume'
        dat['png'] = fname
        data.append(dat)

    #tar.close()

def phonon_thermo_plots(self, df, composition, contentpath, data):
    """
    Function to call all other plot generation functions for thermo data.
    """
    self.phonon_gibbs_plot(df, composition, contentpath, data, uc_unit='eV', plot_unit='eV/atom')
    self.phonon_entropy_plot(df, composition, contentpath, data, uc_unit='J/mol', plot_unit='J/K/mol')
    self.phonon_cp_poly_plot(df, composition, contentpath, data, uc_unit='J/mol', plot_unit='J/K/mol')
    self.phonon_cp_num_plot(df, composition, contentpath, data, uc_unit='J/mol', plot_unit='J/K/mol')
    self.phonon_cv_plot(df, composition, contentpath, data, uc_unit='J/mol', plot_unit='J/K/mol')
    self.phonon_volume_plot(df, composition, contentpath, data, uc_unit='angstrom^3', plot_unit='&#197;^3/atom')
    self.phonon_expansion_plot(df, composition, contentpath, data)
    self.phonon_bulk_plot(df, composition, contentpath, data, uc_unit='GPa', plot_unit='GPa')
    
def phonon_gibbs_plot(self, df, composition, contentpath, data, uc_unit='eV', plot_unit='eV/atom'):
    
    # Initialize plot and table
    fig = go.Figure()
    pngfile = f'phonon.{composition}.G.png'
    csvfile = f'phonon.{composition}.G.csv'
    htmlfile = f'phonon.{composition}.G.html'
    csv_df = {}
    
    lineformats = self.plotly_line_formats
    
    sorted_df = df.sort_values('potential_energy')
    min_series =  None
    for index in sorted_df.index:
        series = sorted_df.loc[index]
        if pd.isna(series.qha):
            continue
        else:
            min_series = series
            break
    if min_series is None:
        fig.data = []
        return None

    csv_df['temperature'] = min_series.qha.T
    ref_G = uc.get_in_units(min_series.qha.G, uc_unit)
    
    # Loop over results
    count = 0
    for i, index in enumerate(df.sort_values(['prototype', 'a']).index):
        series = df.loc[index]
        qha = series.qha
        if pd.isna(qha):
            continue 
        label = f'{series.prototype} a={series.a:.4f}'
        lineformat = lineformats.iloc[i]

        try:
            G = uc.get_in_units(qha.G, uc_unit)
            fig.add_trace(go.Scatter(x=qha.T, y=G - ref_G,
                                     mode='lines',
                                     name=series.prototype,
                                     showlegend=True,
                                     line=dict(
                                         color=lineformat.color,
                                         dash=lineformat.line)))
            
            csv_df[label] = G
            count += 1
        except:
            pass
        
    if count > 0:
        
        fig.update_layout(
            title=dict(
                text="Phonon/QHA Predictions",
                font=dict(size=14),
            ),
            xaxis=dict(
                title=dict(
                    text="Temperature (K)"
                )
            ),
            yaxis=dict(
                title=dict(
                    text=f"&#916;Gibbs ({plot_unit})"
                )
            ),
            paper_bgcolor='white',
            plot_bgcolor='white',
        )
        fig.update_xaxes(
            range=[0, 1000],
            **self.plotly_axes_settings
        )
        fig.update_yaxes(
            **self.plotly_axes_settings
        )

        fig.write_image(Path(contentpath, pngfile), width=1200, height=600,) 
        fig.write_html(Path(contentpath, htmlfile), include_plotlyjs='cdn', full_html=False)
        
        # Save csv table
        csv_df = pd.DataFrame(csv_df)
        csv_df.to_csv(Path(contentpath, csvfile))
    
        # Collect data for web generation
        dat = {}
        dat['composition'] = composition
        dat['name'] = 'Gibbs'
        dat['html'] = htmlfile
        dat['png'] = pngfile
        dat['csv'] = csvfile
        data.append(dat)
            
    fig.data = []

def phonon_entropy_plot(self, df, composition, contentpath, data, uc_unit='J/mol', plot_unit='J/K/mol'):
    
    # Initialize plot and table
    fig = go.Figure()
    pngfile = f'phonon.{composition}.S.png'
    csvfile = f'phonon.{composition}.S.csv'
    htmlfile = f'phonon.{composition}.S.html'
    csv_df = {}

    lineformats = self.plotly_line_formats

    for index in df.index:
        series = df.loc[index]
        if pd.isna(series.qha):
            continue
        else:
            csv_df['temperature'] = series.qha.T
            break
    if 'temperature' not in csv_df:
        fig.data = []
        return None
    
    # Loop over results
    count = 0
    for i, index in enumerate(df.sort_values(['prototype', 'a']).index):
        series = df.loc[index]
        qha = series.qha
        if pd.isna(qha):
            continue 
        label = f'{series.prototype} a={series.a:.4f}'
        lineformat = lineformats.iloc[i]
        
        try:
            S = uc.get_in_units(qha.S, uc_unit)
            fig.add_trace(go.Scatter(x=qha.T, y=S,
                                     mode='lines',
                                     name=series.prototype,
                                     showlegend=True,
                                     line=dict(
                                         color=lineformat.color,
                                         dash=lineformat.line)))
            
            csv_df[label] = S            
            count += 1
        except:
            pass
        
    # Save plot and csv if results exist
    if count > 0:
      
        fig.update_layout(
            title=dict(
                text="Phonon/QHA Predictions",
                font=dict(size=14),
            ),
            xaxis=dict(
                title=dict(
                    text="Temperature (K)"
                )
            ),
            yaxis=dict(
                title=dict(
                    text=f"Entropy ({plot_unit})"
                )
            ),
            paper_bgcolor='white',
            plot_bgcolor='white',
        )
        fig.update_xaxes(
            range=[0, 1000],
            **self.plotly_axes_settings
        )
        fig.update_yaxes(
            rangemode="nonnegative",
            **self.plotly_axes_settings
        )
        fig.write_image(Path(contentpath, pngfile), width=1200, height=600,) 
        fig.write_html(Path(contentpath, htmlfile), include_plotlyjs='cdn', full_html=False)
        
        csv_df = pd.DataFrame(csv_df)
        csv_df.to_csv(Path(contentpath, csvfile))
    
       # Collect data for web generation
        dat = {}
        dat['composition'] = composition
        dat['name'] = 'Entropy'
        dat['html'] = htmlfile
        dat['png'] = pngfile
        dat['csv'] = csvfile
        data.append(dat)
            
    fig.data = []
    
def phonon_cp_poly_plot(self, df, composition, contentpath, data, uc_unit='J/mol', plot_unit='J/K/mol'):
    
    # Initialize plot and table
    fig = go.Figure()
    pngfile = f'phonon.{composition}.Cp-poly.png'
    csvfile = f'phonon.{composition}.Cp-poly.csv'
    htmlfile = f'phonon.{composition}.Cp-poly.html'
    csv_df = {}

    lineformats = self.plotly_line_formats
    
    for index in df.index:
        series = df.loc[index]
        if pd.isna(series.qha):
            continue
        else:
            csv_df['temperature'] = series.qha.T
            break
    if 'temperature' not in csv_df:
        fig.data = []
        return None
    
    # Loop over results
    count = 0
    for i, index in enumerate(df.sort_values(['prototype', 'a']).index):
        series = df.loc[index]
        qha = series.qha
        if pd.isna(qha):
            continue 
        label = f'{series.prototype} a={series.a:.4f}'
        lineformat = lineformats.iloc[i]
        
        try:
            Cp = uc.get_in_units(qha.Cp_poly, uc_unit)
            fig.add_trace(go.Scatter(x=qha.T, y=Cp,
                                     mode='lines',
                                     name=series.prototype,
                                     showlegend=True,
                                     line=dict(
                                         color=lineformat.color,
                                         dash=lineformat.line)))
            
            csv_df[label] = Cp            
            count += 1
        except:
            pass
        
    # Save plot and csv if results exist
    if count > 0:

        fig.update_layout(
            title=dict(
                text="Phonon/QHA Predictions",
                font=dict(size=14),
            ),
            xaxis=dict(
                title=dict(
                    text="Temperature (K)"
                )
            ),
            yaxis=dict(
                title=dict(
                    text=f"Cp polyfit ({plot_unit})",
                )
            ),
            paper_bgcolor='white',
            plot_bgcolor='white',
        )
        fig.update_xaxes(
            range=[0, 1000],
            **self.plotly_axes_settings
        )
        fig.update_yaxes(
            rangemode="nonnegative",
            **self.plotly_axes_settings
        )
        fig.write_image(Path(contentpath, pngfile), width=1200, height=600,) 
        fig.write_html(Path(contentpath, htmlfile), include_plotlyjs='cdn', full_html=False)
        
        csv_df = pd.DataFrame(csv_df)
        csv_df.to_csv(Path(contentpath, csvfile))
    
       # Collect data for web generation
        dat = {}
        dat['composition'] = composition
        dat['name'] = 'Cp polyfit'
        dat['html'] = htmlfile
        dat['png'] = pngfile
        dat['csv'] = csvfile
        data.append(dat)
            
    fig.data = []
    
def phonon_cp_num_plot(self, df, composition, contentpath, data, uc_unit='J/mol', plot_unit='J/K/mol'):
    
    # Initialize plot and table
    fig = go.Figure()
    pngfile = f'phonon.{composition}.Cp-num.png'
    csvfile = f'phonon.{composition}.Cp-num.csv'
    htmlfile = f'phonon.{composition}.Cp-num.html'
    csv_df = {}

    lineformats = self.plotly_line_formats
    
    for index in df.index:
        series = df.loc[index]
        if pd.isna(series.qha):
            continue
        else:
            csv_df['temperature'] = series.qha.T
            break
    if 'temperature' not in csv_df:
        fig.data = []
        return None
    
    # Loop over results
    count = 0
    for i, index in enumerate(df.sort_values(['prototype', 'a']).index):
        series = df.loc[index]
        qha = series.qha
        if pd.isna(qha):
            continue 
        label = f'{series.prototype} a={series.a:.4f}'
        lineformat = lineformats.iloc[i]
        
        try:
            Cp = uc.get_in_units(qha.Cp_num, uc_unit)
            fig.add_trace(go.Scatter(x=qha.T, y=Cp,
                                     mode='lines',
                                     name=series.prototype,
                                     showlegend=True,
                                     line=dict(
                                         color=lineformat.color,
                                         dash=lineformat.line)))
            
            csv_df[label] = Cp            
            count += 1
        except:
            pass
        
    # Save plot and csv if results exist
    if count > 0:

        fig.update_layout(
            title=dict(
                text="Phonon/QHA Predictions",
                font=dict(size=14),
            ),
            xaxis=dict(
                title=dict(
                    text="Temperature (K)"
                )
            ),
            yaxis=dict(
                title=dict(
                    text=f"Cp numerical ({plot_unit})",
                )
            ),
            paper_bgcolor='white',
            plot_bgcolor='white',
        )
        fig.update_xaxes(
            range=[0, 1000],
            **self.plotly_axes_settings
        )
        fig.update_yaxes(
            rangemode="nonnegative",
            **self.plotly_axes_settings
        )
        fig.write_image(Path(contentpath, pngfile), width=1200, height=600,) 
        fig.write_html(Path(contentpath, htmlfile), include_plotlyjs='cdn', full_html=False)
        
        csv_df = pd.DataFrame(csv_df)
        csv_df.to_csv(Path(contentpath, csvfile))
    
       # Collect data for web generation
        dat = {}
        dat['composition'] = composition
        dat['name'] = 'Cp numerical'
        dat['html'] = htmlfile
        dat['png'] = pngfile
        dat['csv'] = csvfile
        data.append(dat)
            
    fig.data = []
    
def phonon_cv_plot(self, df, composition, contentpath, data, uc_unit='J/mol', plot_unit='J/K/mol'):
    
    # Initialize plot and table
    fig = go.Figure()
    pngfile = f'phonon.{composition}.Cv.png'
    csvfile = f'phonon.{composition}.Cv.csv'
    htmlfile = f'phonon.{composition}.Cv.html'
    csv_df = {}

    lineformats = self.plotly_line_formats
    
    for index in df.index:
        series = df.loc[index]
        if pd.isna(series.qha):
            continue
        else:
            csv_df['temperature'] = series.qha.T
            break
    if 'temperature' not in csv_df:
        fig.data = []
        return None
    
    # Loop over results
    count = 0
    for i, index in enumerate(df.sort_values(['prototype', 'a']).index):
        series = df.loc[index]
        qha = series.qha
        if pd.isna(qha):
            continue 
        label = f'{series.prototype} a={series.a:.4f}'
        lineformat = lineformats.iloc[i]
        
        try:
            Cv = uc.get_in_units(qha.Cv, uc_unit)
            fig.add_trace(go.Scatter(x=qha.T, y=Cv,
                                     mode='lines',
                                     name=series.prototype,
                                     showlegend=True,
                                     line=dict(
                                         color=lineformat.color,
                                         dash=lineformat.line)))
            
            csv_df[label] = Cv            
            count += 1
        except:
            pass
        
    # Save plot and csv if results exist
    if count > 0:

        fig.update_layout(
            title=dict(
                text="Phonon/QHA Predictions",
                font=dict(size=14),
            ),
            xaxis=dict(
                title=dict(
                    text="Temperature (K)"
                )
            ),
            yaxis=dict(
                title=dict(
                    text=f"Cv ({plot_unit})",
                )
            ),
            paper_bgcolor='white',
            plot_bgcolor='white',
        )
        fig.update_xaxes(
            range=[0, 1000],
            **self.plotly_axes_settings
        )
        fig.update_yaxes(
            rangemode="nonnegative",
            **self.plotly_axes_settings
        )
        fig.write_image(Path(contentpath, pngfile), width=1200, height=600,) 
        fig.write_html(Path(contentpath, htmlfile), include_plotlyjs='cdn', full_html=False)
        
        csv_df = pd.DataFrame(csv_df)
        csv_df.to_csv(Path(contentpath, csvfile))
    
       # Collect data for web generation
        dat = {}
        dat['composition'] = composition
        dat['name'] = 'Cv'
        dat['html'] = htmlfile
        dat['png'] = pngfile
        dat['csv'] = csvfile
        data.append(dat)
            
    fig.data = []
    
def phonon_volume_plot(self, df, composition, contentpath, data, uc_unit='angstrom^3', plot_unit='$\AA^3$/atom'):
    
    # Initialize plot and table
    fig = go.Figure()
    pngfile = f'phonon.{composition}.V.png'
    csvfile = f'phonon.{composition}.V.csv'
    htmlfile = f'phonon.{composition}.V.html'
    csv_df = {}

    lineformats = self.plotly_line_formats
    
    for index in df.index:
        series = df.loc[index]
        if pd.isna(series.qha):
            continue
        else:
            csv_df['temperature'] = series.qha.T
            break
    if 'temperature' not in csv_df:
        fig.data = []
        return None
    
    # Loop over results
    count = 0
    for i, index in enumerate(df.sort_values(['prototype', 'a']).index):
        series = df.loc[index]
        qha = series.qha
        if pd.isna(qha):
            continue 
        label = f'{series.prototype} a={series.a:.4f}'
        lineformat = lineformats.iloc[i]
        
        try:
            V = uc.get_in_units(qha.V, uc_unit)
            fig.add_trace(go.Scatter(x=qha.T, y=V,
                                     mode='lines',
                                     name=series.prototype,
                                     showlegend=True,
                                     line=dict(
                                         color=lineformat.color,
                                         dash=lineformat.line)))
            
            csv_df[label] = V            
            count += 1
        except:
            pass
        
    # Save plot and csv if results exist
    if count > 0:

        fig.update_layout(
            title=dict(
                text="Phonon/QHA Predictions",
                font=dict(size=14),
            ),
            xaxis=dict(
                title=dict(
                    text="Temperature (K)"
                )
            ),
            yaxis=dict(
                title=dict(
                    text=f"Volume ({plot_unit})",
                )
            ),
            paper_bgcolor='white',
            plot_bgcolor='white',
        )
        fig.update_xaxes(
            range=[0, 1000],
            **self.plotly_axes_settings
        )
        fig.update_yaxes(
            **self.plotly_axes_settings
        )
        fig.write_image(Path(contentpath, pngfile), width=1200, height=600,) 
        fig.write_html(Path(contentpath, htmlfile), include_plotlyjs='cdn', full_html=False)
        
        csv_df = pd.DataFrame(csv_df)
        csv_df.to_csv(Path(contentpath, csvfile))
    
       # Collect data for web generation
        dat = {}
        dat['composition'] = composition
        dat['name'] = 'Volume'
        dat['html'] = htmlfile
        dat['png'] = pngfile
        dat['csv'] = csvfile
        data.append(dat)
            
    fig.data = []
    
def phonon_expansion_plot(self, df, composition, contentpath, data):
    
    # Initialize plot and table
    fig = go.Figure()
    pngfile = f'phonon.{composition}.alpha.png'
    csvfile = f'phonon.{composition}.alpha.csv'
    htmlfile = f'phonon.{composition}.alpha.html'
    csv_df = {}

    lineformats = self.plotly_line_formats
    
    for index in df.index:
        series = df.loc[index]
        if pd.isna(series.qha):
            continue
        else:
            csv_df['temperature'] = series.qha.T
            break
    if 'temperature' not in csv_df:
        fig.data = []
        return None
    
    # Loop over results
    count = 0
    for i, index in enumerate(df.sort_values(['prototype', 'a']).index):
        series = df.loc[index]
        qha = series.qha
        if pd.isna(qha):
            continue 
        label = f'{series.prototype} a={series.a:.4f}'
        lineformat = lineformats.iloc[i]
        
        try:
            alpha = qha.alpha
            fig.add_trace(go.Scatter(x=qha.T, y=alpha,
                                     mode='lines',
                                     name=series.prototype,
                                     showlegend=True,
                                     line=dict(
                                         color=lineformat.color,
                                         dash=lineformat.line)))
            
            csv_df[label] = alpha           
            count += 1
        except:
            pass
        
    # Save plot and csv if results exist
    if count > 0:

        fig.update_layout(
            title=dict(
                text="Phonon/QHA Predictions",
                font=dict(size=14),
            ),
            xaxis=dict(
                title=dict(
                    text="Temperature (K)"
                )
            ),
            yaxis=dict(
                title=dict(
                    text="Thermal expansion"
                )
            ),
            paper_bgcolor='white',
            plot_bgcolor='white',
        )
        fig.update_xaxes(
            range=[0, 1000],
            **self.plotly_axes_settings
        )
        fig.update_yaxes(
            range=[0, None],
            **self.plotly_axes_settings
        )
        fig.write_image(Path(contentpath, pngfile), width=1200, height=600,) 
        fig.write_html(Path(contentpath, htmlfile), include_plotlyjs='cdn', full_html=False)
        
        csv_df = pd.DataFrame(csv_df)
        csv_df.to_csv(Path(contentpath, csvfile))
    
       # Collect data for web generation
        dat = {}
        dat['composition'] = composition
        dat['name'] = 'Thermal expansion'
        dat['html'] = htmlfile
        dat['png'] = pngfile
        dat['csv'] = csvfile
        data.append(dat)
            
    fig.data = []
    
def phonon_bulk_plot(self, df, composition, contentpath, data, uc_unit='GPa', plot_unit='GPa'):
    
    # Initialize plot and table
    fig = go.Figure()
    pngfile = f'phonon.{composition}.B.png'
    csvfile = f'phonon.{composition}.B.csv'
    htmlfile = f'phonon.{composition}.B.html'
    csv_df = {}

    lineformats = self.plotly_line_formats
    
    for index in df.index:
        series = df.loc[index]
        if pd.isna(series.qha):
            continue
        else:
            csv_df['temperature'] = series.qha.T
            break
    if 'temperature' not in csv_df:
        fig.data = []
        return None
    
    # Loop over results
    count = 0
    for i, index in enumerate(df.sort_values(['prototype', 'a']).index):
        series = df.loc[index]
        qha = series.qha
        if pd.isna(qha):
            continue 
        label = f'{series.prototype} a={series.a:.4f}'
        lineformat = lineformats.iloc[i]
        
        try:
            B = uc.get_in_units(qha.B, uc_unit)
            fig.add_trace(go.Scatter(x=qha.T, y=B,
                                     mode='lines',
                                     name=series.prototype,
                                     showlegend=True,
                                     line=dict(
                                         color=lineformat.color,
                                         dash=lineformat.line)))
            
            csv_df[label] = B            
            count += 1
        except:
            pass
        
    # Save plot and csv if results exist
    if count > 0:

        fig.update_layout(
            title=dict(
                text="Phonon/QHA Predictions",
                font=dict(size=14),
            ),
            xaxis=dict(
                title=dict(
                    text="Temperature (K)"
                )
            ),
            yaxis=dict(
                title=dict(
                    text=f"Bulk modulus ({plot_unit})",
                )
            ),
            paper_bgcolor='white',
            plot_bgcolor='white',
        )
        fig.update_xaxes(
            range=[0, 1000],
            **self.plotly_axes_settings
        )
        fig.update_yaxes(
            **self.plotly_axes_settings
        )
        fig.write_image(Path(contentpath, pngfile), width=1200, height=600,) 
        fig.write_html(Path(contentpath, htmlfile), include_plotlyjs='cdn', full_html=False)
        
        csv_df = pd.DataFrame(csv_df)
        csv_df.to_csv(Path(contentpath, csvfile))
    
       # Collect data for web generation
        dat = {}
        dat['composition'] = composition
        dat['name'] = 'Bulk modulus'
        dat['html'] = htmlfile
        dat['png'] = pngfile
        dat['csv'] = csvfile
        data.append(dat)
            
    fig.data = []