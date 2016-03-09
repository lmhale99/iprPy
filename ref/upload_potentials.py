
#This script uploads the data models for LAMMPS implemented potentials 
#to an instance of the Materials Data Curation System

import glob
import requests
import os
import mdcs
from DataModelDict import DataModelDict

#MDCS user name (default is admin)
MDCS_USER = 'lmh1'
#MDCS_USER = "admin"

#MDCS user password (default is admin)
#MDCS_PSWD = "admin"
MDCS_PSWD = "theke+A3upU3"

#MDCS url address (local is http://127.0.0.1:8000)
#MDCS_URL = "http://127.0.0.1:8000"
MDCS_URL = "https://iprhub.nist.gov"

#MDCS template name
TEMPLATE = "LAMMPS-potential"

#Find all json files and xml files in the potentials directory
for json_file in glob.iglob("potentials/*.json"):
    name = os.path.basename(json_file)[:-5]
    
    records = mdcs.explore.query(MDCS_URL, MDCS_USER, MDCS_PSWD,
                                 cert = 'cert', query = str({'title': name}))
    
    if len(records) != 0:
        print name, 'already exists.'
    
    else:
        with open(json_file) as f:
            model = DataModelDict(f)
        xml_file = os.path.join('potentials', name + '.xml')
        with open(xml_file, 'w') as f:
            model.xml(fp=f, indent=2)
        
        response = mdcs.curate_as(xml_file, name, 
                                  MDCS_URL, MDCS_USER, MDCS_PSWD,
                                  cert = 'cert', template_title = TEMPLATE) 
                                  
        if response != 201:
            raise ValueError(name + '\n' + str(response))
        