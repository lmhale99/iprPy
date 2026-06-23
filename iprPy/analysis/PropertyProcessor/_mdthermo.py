# coding: utf-8

# Standard Python libraries
from pathlib import Path
from datetime import date
from math import floor, ceil
import warnings

# http://www.numpy.org/
import numpy as np

# https://pandas.pydata.org/
import pandas as pd

# https://plotly.com/python
import plotly.graph_objects as go

import dbliquid
from atomman import Box, ElasticConstants
import atomman.unitconvert as uc

# Local imports
from ... import load_record
from ...tools import num_deriv_3_point



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
    outputpath = self.outputpath

    # Loop over all props
    num_updated = 0
    num_skipped = 0
    for prop, getkwargs in self.iter_by_prop():
        pot_id = prop.potential_id
        imp_id = prop.potential_LAMMPS_id
    
        # Skip records with existing results
        if prop.mdthermo.exists and runall is False:
            print('skipped')
            num_skipped += 1
            continue
        else:
            # reset data
            prop.mdliquid.compositions.clear()
    
        # Get solid and liquid results
        all_solid_df = database.get_records_df(style='md_solid_properties',
                                            **getkwargs)
        if len(all_solid_df) > 0:
            all_solid_df = all_solid_df[np.isclose(all_solid_df['Pxx (GPa)'], 0.0)]

        all_liquid_df = database.get_records_df(style='md_liquid_properties',
                                            **getkwargs)
        if len(all_liquid_df) > 0:
            all_liquid_df = all_liquid_df[np.isclose(all_liquid_df['P (MPa)'], 0.0)]

        if len(all_solid_df) == 0 and len(all_liquid_df) == 0:   
            print('no finished records')
            continue
        if 'G (eV/atom)' not in all_solid_df and 'G (eV/atom)' not in all_liquid_df:
            print('no thermo results')
            continue
        
        # Add keys if needed
        if 'G (eV/atom)' not in all_solid_df:
            all_solid_df['G (eV/atom)'] = np.nan
        if 'G (eV/atom)' not in all_liquid_df:
            all_liquid_df['G (eV/atom)'] = np.nan

        # Add prototype field to solid data
        self.identify_prototypes(all_solid_df)

        compositions = np.unique(all_solid_df.composition.tolist() + all_liquid_df.composition.tolist())
        
        # Loop over compositions
        for composition in compositions:
            solid_df = all_solid_df[all_solid_df.composition == composition]
            liquid_df = all_liquid_df[all_liquid_df.composition == composition]
            # Build and save plots and tables
            self.mdthermo_plots(solid_df, liquid_df, outputpath, pot_id, imp_id,
                                composition)
            
            # Add composition listing to PotentialProperties content
            prop.mdthermo.compositions.append(composition)

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
                   composition):
    """
    Function to call all plot generation functions for thermo data.
    """
    contentpath = Path(outputpath, potential, implementation)
    if not contentpath.exists():
        contentpath.mkdir(parents=True)


    self.mdthermo_energy_plot(solid_df, liquid_df, composition, contentpath, 
                              uc_unit='eV', plot_unit='eV/atom')
    self.mdthermo_gibbs_plot(solid_df, liquid_df, composition, contentpath,
                             uc_unit='eV', plot_unit='eV/atom')
    self.mdthermo_entropy_plot(solid_df, liquid_df, composition, contentpath,
                               uc_unit='J/mol', plot_unit='J/K/mol')
    self.mdthermo_cp_plot(solid_df, liquid_df, composition, contentpath,
                          uc_unit='J/mol', plot_unit='J/K/mol')
    self.mdthermo_volume_plot(solid_df, liquid_df, composition, contentpath,
                              uc_unit='angstrom^3', plot_unit='&#197;^3/atom')


def mdthermo_energy_plot(self,
                         solid_df,
                         liquid_df,
                         composition,
                         contentpath,
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
        v[~sorted_df.isliquid] = np.nan
        values['liquid'] = np.hstack([[np.nan]*round(sorted_df['T (K)'].values[0] / 50), v])

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
            
    fig.data = []

def mdthermo_gibbs_plot(self,
                        solid_df,
                        liquid_df,
                        composition,
                        contentpath,
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
    min_G0 = 9999999
    min_tag = None
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

            if values[tag][0] < min_G0:
                min_tag = tag
                min_G0 = values[tag][0]

            if Tmax < parsed_df['T (K)'].values[-1]:
                Tmax = parsed_df['T (K)'].values[-1]
            
    # Add liquid
    if len(liquid_df) > 0:
        sorted_df = liquid_df.sort_values('T (K)')
        v = sorted_df['G (eV/atom)'].values
        v[~sorted_df.isliquid] = np.nan
        values['liquid'] = np.hstack([[np.nan]*round(sorted_df['T (K)'].values[0] / 50), v])

        if Tmax < sorted_df['T (K)'].values[-1]:
            Tmax = sorted_df['T (K)'].values[-1]
    
    if len(values) == 0:
        return

    # Build table
    table_df = build_table(values, Tmax, uc_unit)
    # Loop over results
    ylabel = f"Gibbs ({plot_unit})"
    for i, tag in enumerate(values.keys()):
        if min_tag is None:
            yvals = table_df[tag].values
            ylabel = f"Gibbs ({plot_unit})"
        else:
            yvals = table_df[tag].values - table_df[min_tag].values
            ylabel = f"&#916;Gibbs ({plot_unit})"

        lineformat = lineformats.iloc[i]

        # Define plot lines
        fig.add_trace(
            go.Scatter(
                x=table_df.temperature,
                y=yvals,
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
                text=ylabel
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
            
    fig.data = []


def mdthermo_entropy_plot(self,
                         solid_df,
                         liquid_df,
                         composition,
                         contentpath,
                         uc_unit='J/mol',
                         plot_unit='J/K/mol'):
    
    # Initialize plot and table
    fig = go.Figure()
    pngfile = f'mdthermo.{composition}.S.png'
    csvfile = f'mdthermo.{composition}.S.csv'
    htmlfile = f'mdthermo.{composition}.S.html'

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
            G = parsed_df['G (eV/atom)'].values
            H = parsed_df['H (eV/atom)'].values
            T = parsed_df['T (K)'].values
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                values[tag] = (H - G) / T

            if Tmax < parsed_df['T (K)'].values[-1]:
                Tmax = parsed_df['T (K)'].values[-1]
            
    # Add liquid
    if len(liquid_df) > 0:
        sorted_df = liquid_df.sort_values('T (K)')
        G = sorted_df['G (eV/atom)'].values
        H = sorted_df['H (eV/atom)'].values
        T = sorted_df['T (K)'].values
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            v = (H - G) / T
        v[~sorted_df.isliquid] = np.nan
        values['liquid'] = np.hstack([[np.nan]*round(sorted_df['T (K)'].values[0] / 50), v])

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
            text="Entropy vs. Temperature",
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
        range=[0, Tmax],
        **self.plotly_axes_settings
    )
    fig.update_yaxes(
        **self.plotly_axes_settings
    )
    fig.write_image(Path(contentpath, pngfile), width=1200, height=600,) 
    fig.write_html(Path(contentpath, htmlfile), include_plotlyjs='cdn', full_html=False)
    table_df.to_csv(Path(contentpath, csvfile), index=False)
            
    fig.data = []

def mdthermo_cp_plot(self,
                         solid_df,
                         liquid_df,
                         composition,
                         contentpath,
                         uc_unit='J/mol',
                         plot_unit='J/K/mol'):
    
    # Initialize plot and table
    fig = go.Figure()
    pngfile = f'mdthermo.{composition}.Cp.png'
    csvfile = f'mdthermo.{composition}.Cp.csv'
    htmlfile = f'mdthermo.{composition}.Cp.html'

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
            if len(parsed_df) < 3:
                continue
            H = parsed_df['H (eV/atom)'].values
            T = parsed_df['T (K)'].values
            values[tag] = num_deriv_3_point(T, H)

            if Tmax < parsed_df['T (K)'].values[-1]:
                Tmax = parsed_df['T (K)'].values[-1]
            
    # Add liquid
    if len(liquid_df) >= 3:
        sorted_df = liquid_df.sort_values('T (K)')
        H = sorted_df['H (eV/atom)'].values
        T = sorted_df['T (K)'].values
        v = num_deriv_3_point(T, H)
        v[~sorted_df.isliquid] = np.nan
        values['liquid'] = np.hstack([[np.nan]*round(sorted_df['T (K)'].values[0] / 50), v])

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
            text="Constant P Heat Capacity vs. Temperature",
            font=dict(size=14),
        ),
        xaxis=dict(
            title=dict(
                text="Temperature (K)"
            )
        ),
        yaxis=dict(
            title=dict(
                text=f"Cp ({plot_unit})"
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
            
    fig.data = []

def mdthermo_volume_plot(self,
                         solid_df,
                         liquid_df,
                         composition,
                         contentpath,
                         uc_unit='angstrom^3',
                         plot_unit='&#197;^3/atom'):
    
    def get_volume(series):
        box = Box(a=series.a, b=series.b, c=series.c, alpha=series.alpha, beta=series.beta, gamma=series.gamma)
        return box.volume

    # Initialize plot and table
    fig = go.Figure()
    pngfile = f'mdthermo.{composition}.V.png'
    csvfile = f'mdthermo.{composition}.V.csv'
    htmlfile = f'mdthermo.{composition}.V.html'

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
            values[tag] = parsed_df.apply(get_volume, axis=1)

            if Tmax < parsed_df['T (K)'].values[-1]:
                Tmax = parsed_df['T (K)'].values[-1]
            
    # Add liquid
    if len(liquid_df) > 0:
        sorted_df = liquid_df.sort_values('T (K)')
        v = uc.set_in_units(sorted_df['V (m^3)'].values, 'm^3')
        v[~sorted_df.isliquid] = np.nan
        values['liquid'] = np.hstack([[np.nan]*round(sorted_df['T (K)'].values[0] / 50), v])

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
            text="Volume vs. Temperature",
            font=dict(size=14),
        ),
        xaxis=dict(
            title=dict(
                text="Temperature (K)"
            )
        ),
        yaxis=dict(
            title=dict(
                text=f"Volume ({plot_unit})"
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
            
    fig.data = []


def build_table(values, Tmax, uc_unit):

    Tvalues = np.arange(0, Tmax+50, 50, dtype=float)
    
    # Build table
    table_df = {}
    table_df['temperature'] = Tvalues
    for tag in values:
        table_df[tag] = np.full_like(Tvalues, np.nan)
        if len(values[tag]) > 0:
            table_df[tag][:len(values[tag])] = uc.get_in_units(values[tag], uc_unit)
    table_df = pd.DataFrame(table_df)

    return table_df