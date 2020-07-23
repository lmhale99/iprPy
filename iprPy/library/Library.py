# coding: utf-8
# Standard Python libraries
from pathlib import Path
import uuid

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# https://github.com/usnistgov/atomman
import atomman as am

import potentials

import requests

from .. import Settings, load_record
from ..tools import aslist

class Library():
    """
    Class for interacting with the iprPy library directory.
    """
    def __init__(self, directory=None, load=False, local=True, remote=True):
        """
        Class initializer

        Parameters
        ----------
        directory : str or Path, optional
            The path to the library directory to interact with.  If not given,
            will use the library directory that has been set for iprPy.
        """
        if directory is None:
            self.__directory = Settings().library_directory
        else:
            self.__directory = Path(directory).resolve()

        self.__potdb = potentials.Database(localpath=self.directory,
                                           local=local, remote=remote,
                                           load=load)

    @property
    def directory(self):
        return self.__directory

    @property
    def potdb(self):
        return self.__potdb

    @property
    def all_ref_styles(self):
        """list : all reference record styles hosted at potentials.nist.gov"""
        return ['crystal_prototype', 'dislocation', 'free_surface', 'point_defect', 'stacking_fault', 'potential_LAMMPS']

    def download_refs(self, style=None, status='active'):
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
        # Get all_ref_styles if none are specified
        if style is None:
            style = self.all_ref_styles
        style = aslist(style)
        
        for s in style:
            if s == 'potential_LAMMPS':
                self.potdb.download_lammps_potentials(format='json', indent=4, status=status, verbose=True)
            else:
                self.potdb.download_records(s, format='json', indent=4, verbose=True)

    def download_oqmd_crystals(self, elements):
        """
        Accesses OQMD and downloads crystal structures containing the given
        elements.  The structures are saved to the iprPy library as
        reference_crystal records.
        
        Parameters
        ----------
        elements : list
            A list of element symbols.
        """
        # Load record style and set universal values
        style = 'reference_crystal'
        record = load_record(style)
        input_dict = {}
        input_dict['sourcename'] = "Open Quantum Materials Database"
        input_dict['sourcelink'] = "http://oqmd.org/"
        input_dict['length_unit'] = "angstrom"
        
        # Set library subdirectory
        style_directory = Path(self.directory, style)
        if not style_directory.is_dir():
            style_directory.mkdir(parents=True)
        
        # Sort elements
        elements.sort()

        # Build list of downloaded entries
        have = []
        for fname in style_directory.glob('*.json'):
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
            with open(Path(style_directory, entry_id+'.json'), 'w') as f:
                record.content.json(fp=f, indent=4)
            print('Added', entry_id)

    def download_mp_crystals(self, elements, api_key=None):
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
        style_directory = Path(self.directory, style)
        if not style_directory.is_dir():
            style_directory.mkdir(parents=True)
        
        # Sort elements
        elements.sort()

        # Build list of downloaded entries
        have = []
        for fname in style_directory.glob('*.json'):
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
                        with open(Path(style_directory, entry_id+'.json'), 'w') as f:
                            record.content.json(fp=f, indent=4)
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
        content = self.potdb.get_record(template=style, title=name, verbose=verbose)
                
        # Load as iprPy record if style exists
        try:
            return load_record(style, name, content)
        except:
            return content    
        
    def get_potentials(self, id=None, key=None, potid=None, potkey=None,
                    status='active', pair_style=None, element=None,
                    symbol=None, verbose=False, get_files=False):
        """
        Gets LAMMPS potentials from the iprPy library or by downloading from
        potentials.nist.gov if local copies are not found.
        
        Parameters
        ----------
        id : str or list, optional
            The id value(s) to limit the search by.
        key : str or list, optional
            The key value(s) to limit the search by.
        potid : str or list, optional
            The potid value(s) to limit the search by.
        potkey : str or list, optional
            The potkey value(s) to limit the search by.
        status : str or list, optional
            The status value(s) to limit the search by.
        pair_style : str or list, optional
            The pair_style value(s) to limit the search by.
        element : str or list, optional
            The included elemental model(s) to limit the search by.
        symbol : str or list, optional
            The included symbol model(s) to limit the search by.
        verbose: bool, optional
            If True, informative print statements will be used.
        get_files : bool, optional
            If True, then the parameter files for the matching potentials
            will also be retrieved and copied to the working directory.
            If False (default) and the parameter files are in the library,
            then the returned objects' pot_dir path will be set appropriately.
            
        Returns
        -------
        Potential.LAMMPSPotential
            The potential object to use.
        """
        if self.potdb.lammps_potentials is None:
            self.potdb.load_lammps_potentials()
            
        return self.potdb.get_lammps_potentials(id=id, key=key, potid=potid, potkey=potkey,
                                                status=status, pair_style=pair_style, element=element,
                                                symbol=symbol, verbose=verbose, get_files=get_files)

    def get_potential(self, id=None, key=None, potid=None, potkey=None,
                    status='active', pair_style=None, element=None,
                    symbol=None, verbose=False, get_files=False):
        """
        Gets a LAMMPS potential from the iprPy library or by downloading from
        potentials.nist.gov if a local copy is not found.  Will raise an error
        if none or multiple matching potentials are found.
        
        Parameters
        ----------
        id : str or list, optional
            The id value(s) to limit the search by.
        key : str or list, optional
            The key value(s) to limit the search by.
        potid : str or list, optional
            The potid value(s) to limit the search by.
        potkey : str or list, optional
            The potkey value(s) to limit the search by.
        status : str or list, optional
            The status value(s) to limit the search by.
        pair_style : str or list, optional
            The pair_style value(s) to limit the search by.
        element : str or list, optional
            The included elemental model(s) to limit the search by.
        symbol : str or list, optional
            The included symbol model(s) to limit the search by.
        verbose: bool, optional
            If True, informative print statements will be used.
        get_files : bool, optional
            If True, then the parameter files for the matching potentials
            will also be retrieved and copied to the working directory.
            If False (default) and the parameter files are in the library,
            then the returned objects' pot_dir path will be set appropriately.
            
        Returns
        -------
        Potential.LAMMPSPotential
            The potential object to use.
        """
        
        return self.potdb.get_lammps_potential(id=id, key=key, potid=potid, potkey=potkey,
                                               status=status, pair_style=pair_style, element=element,
                                               symbol=symbol, verbose=verbose, get_files=get_files)