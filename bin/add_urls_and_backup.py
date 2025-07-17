# Standard Python libraries
import argparse

import iprPy

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='script to add URL fields to iprPy calculations and copy to backup/public databases')
    parser.add_argument('database', help='name of the primary database where records are to be found')
    parser.add_argument('calc_style', help='style of the calculation to update and copy')
    parser.add_argument('-b', '--base_url',  help='base URL to use for the URL fields',
                        default='https://potentials.nist.gov/pid/rest/local/potentials')
    parser.add_argument('-a', '--alt_databases', nargs='*',
                        help='names of any alternate databases where the changed records are to be copied')
    parser.add_argument('--nocopytar', action='store_true',
                       help='indicates that tar files should not be copied to any alternate databases' )
    args = parser.parse_args()
    
    # Load database(s)
    database = iprPy.load_database(args.database)
    alt_databases = []
    for alt_database_name in args.alt_databases:
        alt_databases.append(iprPy.load_database(alt_database_name))

    iprPy.analysis.add_urls_and_backup(database,
                                       args.calc_style,
                                       base_url = args.base_url,
                                       alt_databases = alt_databases,
                                       copytar = not args.nocopytar)