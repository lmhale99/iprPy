from yabadaba.record import Record, load_record, recordmanager

__all__ = ['Record', 'load_record', 'recordmanager']

# Add the modular Record styles
recordmanager.import_style('PotentialProperties', '.PotentialProperties', __name__)
recordmanager.import_style('md_solid_properties', '.md_solid_properties', __name__)