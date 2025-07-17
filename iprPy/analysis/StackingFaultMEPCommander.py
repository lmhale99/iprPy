import argparse
from typing import Optional, Union

# http://www.numpy.org/
import numpy as np

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.unitconvert as uc

from DataModelDict import DataModelDict as DM

from .. import load_database
from ..database import IprPyDatabase

class StackingFaultMEPCommander():

    def __init__(self,
                 database: Union[str, IprPyDatabase],
                 nameletter: Optional[str] = None,
                 family: Optional[str] = None,
                 stackingfault_id: Optional[str] = None,
                 potential_LAMMPS_id: Optional[str] = None,
                 verbose: bool = False):
        """
        Calculation manager class to evaluate minimum energy paths (MEPs) for
        stacking_fault_map_2D calculation results.  During init, a list of
        calculation records will be built containing any matching calculations
        that are finished but lack MEP results.

        Parameters
        ----------
        database : str or iprPy.database.IprPyDatabase
            The database or name of the database to use.
        nameletter : str or None, optional
            If given, the constructed list of records will only include
            calculations that have names starting with this letter.  As the
            calculation names are UUID4 keys, the first letter can have values
            of 0-9 and a-f.  This can be useful for distributing execution of
            the calculations across multiple commanders/runners.
        family : str or None, optional
            If given, the constructed list of records will only include
            calculations with the given system prototype family.
        stackingfault_id : str or None, optional
            If given, the constructed list of records will only include
            calculations with the given stacking fault type as identified by a
            stackingfault_id value.
        potential_LAMMPS_id : str or None, optional
            If given, the constructed list of records will only include
            calculations that used the indicated LAMMPS potential.
        verbose : bool, optional
            If True, messages will be printed about how many total matching
            calculation records are found for the above settings, and how many
            are missing MEP results.
        """
        
        # Load database if database name is given
        if isinstance(database, str):
            database = load_database(database)
        self.__database = database
        
        # Get all matching finished calculation results
        allrecords = database.get_records(style='calculation_stacking_fault_map_2D',
                                          family=family,
                                          stackingfault_id=stackingfault_id,
                                          potential_LAMMPS_id=potential_LAMMPS_id,
                                          num_a1=30, status='finished')
        
        # Filter records by first letter
        if nameletter is not None:
            records = []
            for record in allrecords:
                if record.name[0] == nameletter:
                    records.append(record)
        else:
            records = allrecords
        
        if verbose:
            print(f'{len(records)} total records found', flush=True)

        # Search for records that don't have MEP results
        self.__records = []
        for record in records:
            try:
                record.paths
            except ValueError:
                self.records.append(record)         
        if verbose:
            print(f'{len(self.records)} records missing MEP results', flush=True)

    @property
    def records(self):
        """list: The calculation records identified that are missing MEP results"""
        return self.__records
    
    @property
    def database(self):
        """iprPy.database.IprPyDatabase: The database to interact with"""
        return self.__database

    def get_path_settings(self, record):
        """
        Get path settings for a record based on its stacking fault type.

        Parameters
        ----------
        sfid : str
            The stacking fault id, giving the crystal prototype family and
            fault plane.
        a1vect : numpy.ndarray
            The a1 shift vector for the gamma surface.  Used to identify the
            ideal initial path guesses.
        a2vect : numpy.ndarray
            The a2 shift vector for the gamma surface.  Used to identify the
            ideal initial path guesses.

        Returns 
        -------
        path_settings: list of dict
            Settings for computing one or more MEPs, where each dict contains
            'direction', 'pos' and 'climbpoints'.  'direction' is a str
            slip path direction tag, 'pos' is an array of end/junction points
            for the initial path guess, and 'climbpoints' indicates how many
            maxima are expected along the path.
        """
        sfid = record.defect.id
        gamma = record.gamma
        a1vect = gamma.a1vect
        a2vect = gamma.a2vect

        if sfid == 'A1--Cu--fcc--100sf':
            return [
                dict(
                    direction = 'a/2 [0 -1 1]',
                    pos = np.array([[0,0,0], a1vect]),
                    climbpoints = 1
                )
            ]

        elif sfid == 'A1--Cu--fcc--111sf':
            return [
                dict(
                    direction = 'a/2 [0 -1 1]',
                    pos = np.array([[0,0,0], (a1vect + a2vect) / 3, a1vect]),
                    climbpoints = 2
                )
            ]
        
        elif sfid == 'A2--W--bcc--110sf':
            return [
                dict(
                    direction = 'a/2 [-1 1 -1]',
                    pos = np.array([[0,0,0], a1vect]),
                    climbpoints = 1
                )
            ]
            
        elif sfid == 'A2--W--bcc--112sf':
            return [
                dict(
                    direction = 'a/2 [-1 -1 1]',
                    pos = np.array([[0,0,0], a1vect]),
                    climbpoints = 1
                )
            ]
        
        elif sfid == 'A2--W--bcc--123sf':
            return [
                dict(
                    direction = 'a/2 [-1 -1 1]',
                    pos = np.array([[0,0,0], a1vect]),
                    climbpoints = 1
                )
            ]
        
        elif sfid == 'A3--Mg--hcp--0001sf':
            return [
                dict(
                    direction = 'a/3 [-2 1 1 0]',
                    pos = np.array([[0,0,0], (a1vect + a2vect) / 3, a1vect]),
                    climbpoints = 2
                )
            ]
            
        elif sfid == 'A3--Mg--hcp--1010sf-1':
            return [
                dict(
                    direction = 'a/3 [-1 2 -1 0]',
                    pos = np.array([[0,0,0], a1vect]),
                    climbpoints = 1
                )
            ]
        
        elif sfid == 'A3--Mg--hcp--1010sf-2':
            return [
                dict(
                    direction = 'a/3 [-1 2 -1 0]',
                    pos = np.array([[0,0,0], a1vect]),
                    climbpoints = 1
                )
            ]
            
        elif sfid == 'A3--Mg--hcp--1011sf-1':
            return [
                dict(
                    direction = 'a/3 [-1 2 -1 0]',
                    pos = np.array([[0,0,0], a1vect]),
                    climbpoints = 1
                ),
                dict(
                    direction = 'a/3 [-2 1 1 3]',
                    pos = np.array([[0,0,0], a2vect]),
                    climbpoints = 1
                )
            ]
        
        elif sfid == 'A3--Mg--hcp--1011sf-2':
            return [
                dict(
                    direction = 'a/3 [-1 2 -1 0]',
                    pos = np.array([[0,0,0], a1vect]),
                    climbpoints = 1
                ),
                dict(
                    direction = 'a/3 [-2 1 1 3]',
                    pos = np.array([[0,0,0], a2vect]),
                    climbpoints = 1
                )
            ]
        
        elif sfid == 'A3--Mg--hcp--2112sf':
            return [
                dict(
                    direction = 'a/3 [-2 1 1 3]',
                    pos = np.array([[0,0,0], a2vect]),
                    climbpoints = 1
                )
            ]
        
        else:
            return []

    def add_intrinsic_fault_energy(self, record):
        """
        Extracts the intrinsic stacking fault energy from a finished
        calculation record's gamma surface, if there is one expected for the
        associated stacking fault type.  The intrinsic energy value is added as
        an element in the record's model contents.

        Parameters
        ----------
        record : iprPy.calculation.StackingFaultMap2D
            A finished stacking fault record to extract the intrinsic stacking
            fault energy from if there is one for the fault type.
        """
        sfid = record.defect.id
        gamma = record.gamma
        calc = record.model['calculation-stacking-fault-map-2D']

        if sfid == 'A1--Cu--fcc--111sf':
            calc['intrinsic-fault-energy'] = uc.model(gamma.E_gsf(a1=1/3, a2=1/3), 'mJ/m^2')

        elif sfid == 'A3--Mg--hcp--0001sf':
            calc['intrinsic-fault-energy'] = uc.model(gamma.E_gsf(a1=1/3, a2=1/3), 'mJ/m^2')

    def mep_relax(self, 
                  gamma: am.defect.GammaSurface,
                  pos: np.ndarray,
                  direction: str,
                  npoints: int = 31,
                  ipoints: int = 1001,
                  relaxsteps: int = 500000,
                  climbsteps: int = 500000,
                  climbpoints: int = 1):
        """
        Parameters
        ----------
        gamma : atomman.defect.GammaSurface
            The gamma surface to compute the MEP path for.
        pos : numpy.ndarray
            The list of end/junction points along the ideal initial path guess.
        direction : str
            The path descriptor/label.
        npoints : int, optional
            The number of discrete points to use for the path during relaxation.
            Default value is 31.
        ipoints : int, optional
            The number of discrete points to use for the path when evaluating the
            ideal shear stress.  Default value is 1001.
        relaxsteps : int, optional
            The maximum number of steps to perform during the relaxation phase of
            the mep evaluation.  Default value is 500000.
        climbsteps : int, optional
            The maximum number of steps to perform during the climbing phase of
            the mep evaluation.  Default value is 500000.
        climbpoints : int, optional
            The expected number of maxima along the energy path.  Default value
            is 1.

        Returns
        -------
        results : DataModelDict.DataModelDict
            A data model of the relaxed slip path results
        """
    
        # Construct initial path for relaxing along ideal
        path = gamma.build_path(pos, npoints)
        
        # Construct fine path along ideal (not for relaxing)
        idealpath = gamma.build_path(pos, ipoints)
        
        # Relax path and create fine interpolation
        path = path.relax(relaxsteps, climbsteps, climbpoints=climbpoints)
        ipath = path.interpolate_path(np.linspace(0.0, path.arccoord[-1], ipoints))
        
        # Create results DM
        results = DM()
        results['direction'] = direction
        results['minimum-energy-path'] = uc.model(path.coord, 'angstrom')
        results['unstable-fault-energy-mep'] = uc.model(ipath.energy().max(), 'mJ/m^2')
        results['unstable-fault-energy-unrelaxed-path'] = uc.model(idealpath.energy().max(), 'mJ/m^2')
        results['ideal-shear-stress-mep'] = uc.model(np.abs(ipath.force).max(), 'GPa')
        results['ideal-shear-stress-unrelaxed-path'] = uc.model(np.abs(idealpath.force).max(), 'GPa')

        return results


    def run_mep(self,
                record,
                npoints: int = 31,
                ipoints: int = 1001,
                relaxsteps: int = 500000,
                climbsteps: int = 500000):
        """
        Performs any needed MEP analyses and extracts any intrinsic stacking
        fault energies for a given calculation record.

        Parameters
        ----------
        record : iprPy.calculation.StackingFaultMap2D
            A finished stacking fault record to check and run MEP analyses for.
        npoints : int, optional
            The number of discrete points to use for the path during relaxation.
            Default value is 31.
        ipoints : int, optional
            The number of discrete points to use for the path when evaluating the
            ideal shear stress.  Default value is 1001.
        relaxsteps : int, optional
            The maximum number of steps to perform during the relaxation phase of
            the mep evaluation.  Default value is 500000.
        climbsteps : int, optional
            The maximum number of steps to perform during the climbing phase of
            the mep evaluation.  Default value is 500000.

        Returns
        -------
        updated : bool
            True if MEP calculations were performed and added to the record's
            model contents for updating in the database.  False means that
            MEP results already exist in the record, or that no path settings
            were found for the fault type therefore no MEPs were evaluated.
        """
        # Check if content already exists
        calc = record.model['calculation-stacking-fault-map-2D']
        if 'slip-path' in calc:
            return False
        
        # Fetch path settings for the record
        path_settings = self.get_path_settings(record)
        if len(path_settings) == 0:
            return False

        print(record.name, flush=True)

        self.add_intrinsic_fault_energy(record)

        gamma = record.gamma
        for settings in path_settings:
            slippath = self.mep_relax(gamma, settings['pos'], settings['direction'],
                                      npoints=npoints, ipoints=ipoints,
                                      relaxsteps=relaxsteps, climbsteps=climbsteps, 
                                      climbpoints=settings['climbpoints'])
            calc.append('slip-path', slippath)

        return True
    
    def runall_mep(self,
                   npoints: int = 31,
                   ipoints: int = 1001,
                   relaxsteps: int = 500000,
                   climbsteps: int = 500000,
                   upload: bool = True):
        """
        Performs any needed MEP analyses and extracts any intrinsic stacking
        fault energies for all records identified when this commander object
        was initialized.

        Parameters
        ----------
        npoints : int, optional
            The number of discrete points to use for the path during relaxation.
            Default value is 31.
        ipoints : int, optional
            The number of discrete points to use for the path when evaluating the
            ideal shear stress.  Default value is 1001.
        relaxsteps : int, optional
            The maximum number of steps to perform during the relaxation phase of
            the mep evaluation.  Default value is 500000.
        climbsteps : int, optional
            The maximum number of steps to perform during the climbing phase of
            the mep evaluation.  Default value is 500000.
        upload : bool, optional
            If True (default), the modified records will be automatically
            updated in the database as the calculations finish.
        """
        for record in self.records:
            updated = self.run_mep(record, npoints=npoints, ipoints=ipoints,
                                   relaxsteps=relaxsteps, climbsteps=climbsteps)
            if upload and updated:
                self.database.update_record(record=record)