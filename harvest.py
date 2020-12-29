'''
The UMedia harvest script aims to find the newly added map items in the specific month.

No manually edit is needed before executing the script. However, at the beginning of the
execution, user needs to input the expected number of results as well as the selected 
year and date with the format like YYYY-MM. After that, the maps that were added in that 
date will be printed out in a csv spreadsheet with the action date you performed.


------------
Original created on Dec 01, 2020
@author: Ziying/Gene Cheng (cheng904@umn.edu)

'''


import json
import time
import csv
import urllib.request
import pandas as pd

## user input
# number of map search results
num = input('Enter the number of results: ')
# assertion to check input format
assert num.isdigit() == True, 'Input number must be a integer.'

# specific year and month
yrmon = input('Enter the selected year and month(e.g. 2020-11): ')
# assertions to check input format: YYYY-MM
assert yrmon.count('-') == 1, 'Input format must be a dash-separated pair of year and month. '
assert len(yrmon.split('-')[0]) == 4, 'Input year must be 4 digits.'
assert len(yrmon.split('-')[1]) == 2, 'Input year must be 2 digits.'


# request map are sorted by latest added with the specific number of maps
req = f'https://umedia.lib.umn.edu/search.json?facets%5Bcontributing_organization_name_s%5D%5B%5D=University+of+Minnesota+Libraries%2C+John+R.+Borchert+Map+Library.&q=borchert&rows={num}&sort=date_added_sort+desc%2C+title_sort+asc'
res = urllib.request.urlopen(req)
data = json.loads(res.read())             


with open('request_data.json', 'w') as f:
    json.dump(data, f)


# fieldnames for output csv file
fieldnames = ['Title', 'Alternative Title', 'Description', 'Language', 'Creator', 'Publisher',
              'Subject', 'Keyword', 'Date Issued', 'Temporal Coverage', 'Date Range',
              'Spatial Coverage', 'Bounding Box', 'Information', 'Download', 'Image', 'Manifest', 
              'Identifier', 'Slug', 'Access Rights', 'Provenance', 'Code', 'Is Part Of', 'Status', 
              'Accrual Method', 'Date Accessioned', 'Rights', 'Genre', 'Type', 'Format', 'Geometry Type',
              'Suppressed', 'Child']      


# dataframe with full metadata from json response
full_df = pd.read_json('request_data.json')
# create an empty dataframe with output csv fieldnames only
out_df = pd.DataFrame(columns=fieldnames)


## extract content from full_df
out_df['Alternative Title'] = full_df['title']
out_df['Description'] = full_df['description'] + ' Dimensions: ' + full_df['dimensions']
out_df['Language'] = full_df['language'].str.join('; ')
out_df['Creator'] = full_df['creator'].str.join('; ')
out_df['Publisher'] = full_df['publisher']
out_df['Keyword'] = full_df['subject'].str.join('|')
out_df['Date Issued'] = full_df['date_created'].str.join('')

# spatial coverage
out_df['Spatial Coverage'] = full_df['city'] + full_df['state']  
out_df['Spatial Coverage'] = out_df['Spatial Coverage'].str.join(', ')      # city, state

out_df['Spatial Coverage'] = out_df['Spatial Coverage'].fillna(full_df['country'].str.join(''))    # replace NaN with country
out_df['Spatial Coverage'] = out_df['Spatial Coverage'].fillna(full_df['continent'].str.join(''))  # replace NaN with continent
out_df['Spatial Coverage'] = out_df['Spatial Coverage'].fillna(full_df['region'].str.join(''))     # replace NaN with region

out_df['Information'] = 'https://umedia.lib.umn.edu/item/' + full_df['id']
out_df['Download'] = 'http://cdm16022.contentdm.oclc.org/utils/getfile/collection/' + full_df['set_spec'] + '/id/' + full_df['parent_id'].astype(str) + '/filename/print/page/download/fparams/forcedownload'
out_df['Image'] = full_df['thumb_url']
out_df['Manifest'] = 'https://cdm16022.contentdm.oclc.org/iiif/info/' + full_df['set_spec'] + '/' + full_df['parent_id'].astype(str) + '/manifest.json'
out_df['Identifier'] = full_df['system_identifier']
out_df['Slug'] = full_df['id']
out_df['Access Rights'] = full_df['local_rights']


## hard-code columns
out_df['Provenance'] = 'University of Minnesota'
out_df['Code'] = '05d-01'
out_df['Is Part Of'] = '05d-01'
out_df['Status'] = 'Active'
out_df['Accrual Method'] = 'Blacklight'
out_df['Rights'] = 'Public'
out_df['Genre'] = 'Maps'
out_df['Type'] = 'Image'
out_df['Format'] = 'JPEG'
out_df['Geometry Type'] = 'Image'
out_df['Suppressed'] = 'FALSE'
out_df['Child'] = 'FALSE'


# export dataframe to csv file
# add the action date to the output filename with the format (YYYYMMDD)
ActionDate = time.strftime('%Y%m%d')
filepath = "reports/allNewItems_%s.csv" % (ActionDate)
out_df.to_csv(filepath, index=False)
print("#### CSV report is created ####")
