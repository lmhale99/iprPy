# coding: utf-8

# https://github.com/usnistgov/atomman
from atomman.library.record import Record, load_record, recordmanager

__all__ = ['Record', 'load_record', 'recordmanager']
__all__.sort()

# Add the modular Record styles
recordmanager.import_style('PotentialProperties', '.PotentialProperties', __name__)
recordmanager.import_style('md_solid_properties', '.MDSolidProperties', __name__)