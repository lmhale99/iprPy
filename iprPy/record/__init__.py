import sys

from atomman.library.record import Record, load_record, recordmanager
__all__ = ['Record', 'load_record', 'recordmanager']

#### Non-calculation records ####

# Import ReferenceCrystal
try:
    from .ReferenceCrystal import ReferenceCrystal
except Exception as e:
    recordmanager.failed_styles['reference_crystal'] = '%s: %s' % sys.exc_info()[:2]
else:
    recordmanager.loaded_styles['reference_crystal'] = ReferenceCrystal
    __all__.append('ReferenceCrystal')

# Import FreeSurface
try:
    from .FreeSurface import FreeSurface
except Exception as e:
    recordmanager.failed_styles['free_surface'] = '%s: %s' % sys.exc_info()[:2]
else:
    recordmanager.loaded_styles['free_surface'] = FreeSurface
    __all__.append('FreeSurface')

# Import StackingFault
try:
    from .StackingFault import StackingFault
except Exception as e:
    recordmanager.failed_styles['stacking_fault'] = '%s: %s' % sys.exc_info()[:2]
else:
    recordmanager.loaded_styles['stacking_fault'] = StackingFault
    __all__.append('StackingFault')

# Import PointDefect
try:
    from .PointDefect import PointDefect
except Exception as e:
    recordmanager.failed_styles['point_defect'] = '%s: %s' % sys.exc_info()[:2]
else:
    recordmanager.loaded_styles['point_defect'] = PointDefect
    __all__.append('PointDefect')

# Import Dislocation
try:
    from .Dislocation import Dislocation
except Exception as e:
    recordmanager.failed_styles['dislocation'] = '%s: %s' % sys.exc_info()[:2]
else:
    recordmanager.loaded_styles['dislocation'] = Dislocation
    __all__.append('Dislocation')

__all__.sort()
