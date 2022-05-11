from yabadaba import databasemanager

from .IprPyDatabase import IprPyDatabase

# Extend the yabadaba MongoDatabase to include IprPyDatabase operations
class MongoDatabase(databasemanager.get_class('mongo'), IprPyDatabase):
    
    
    def check_records(self, record_style=None):
        """
        Counts the number of records of a given style in the database.  If the
        records are calculation records, then it will also list the number of
        calculations with each status value.
        
        Parameters
        ----------
        record_style : str, optional
            The record style to check on.  If not given, then the available record
            styles will be listed and the user prompted to pick one.
        """
        if record_style is None:
            record_style = self.select_record_style()
        
        if record_style is not None:

            # Display information about database records
            count = self.count_records(style=record_style)
            print(f'In {self}:')
            print(f'- {count} of style {record_style}', flush=True)
            
            # Count status values of calculations
            if record_style[:12] == 'calculation_':
                count = self.count_records(style=record_style, status='finished')
                print(f" - {count} finished")
                count = self.count_records(style=record_style, status='not calculated')
                print(f" - {count} not finished")
                count = self.count_records(style=record_style, status='error')
                print(f" - {count} issued errors")