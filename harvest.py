'''
The UMedia harvest script aims to find the newly added map items in a specific date range.
Users need to input a starting date in a YYYY-MM format, and the ending date will be current
date by default. Besides, users need also input the expected number of search results so that
at the beginning of the execution.

A temporary JSON file 'request_YYYYMMDD.json' wll be updated and saved for all search results.
Then it will be split and saved into 'jsons' folder by month within the expected date range.
CSV files in the 'reports' folder are the metadata extracted by thier jsons by month.

------------
Original created on Dec 01, 2020
@author: Ziying/Gene Cheng (cheng904@umn.edu)

updated on May 1st, 2021 by Ziying/Gene Cheng (cheng904@umn.edu)

'''


import json
import time
import csv
import urllib.request
import pandas as pd
from iso639 import Lang

# user input 1: number of map search results
num = input('Enter the number of latest maps: ')
# assertion to check input format
assert num.isdigit() == True, 'Input number must be a integer.'

# user input 2: set date range for search
dateBegin = input('Set a date range from an input YYYY-MM to today: ')
# assertions to check input format: YYYY-MM
assert dateBegin.count('-') == 1, 'Input format must be a dash-separated pair of year and month. '
assert len(dateBegin.split('-')[0]) == 4, 'Input year must be 4 digits.'
assert len(dateBegin.split('-')[1]) == 2, 'Input year must be 2 digits.'


dateEnd = time.strftime('%Y-%m')
months = pd.date_range(dateBegin, dateEnd,freq='M').strftime("%Y-%m").tolist()
if dateEnd not in months:
    months.append(dateEnd)

fieldnames = ['Title', 'Alternative Title', 'Description', 'Language', 'Creator',
              'Resource Type', 'Keyword', 'Date Issued', 'Temporal Coverage', 'Date Range',
              'Spatial Coverage', 'Bounding Box', 'Information', 'Download', 'Image', 'Manifest', 
              'Identifier', 'ID', 'Access Rights', 'Provider', 'Code', 'Member Of', 'Status', 
              'Accrual Method', 'Date Accessioned', 'Rights', 'Resource Class', 'Format',
              'Suppressed', 'Child Record'] 

actionDate = time.strftime('%Y-%m-%d')

# requested maps are sorted by latest added with the specific search numbers
req = f'https://umedia.lib.umn.edu/search.json?facets%5Bcontributing_organization_name_s%5D%5B%5D=University+of+Minnesota+Libraries%2C+John+R.+Borchert+Map+Library.&q=borchert&rows={num}&sort=date_added_sort+desc%2C+title_sort+asc'
print('> Requesting URL ...')
res = urllib.request.urlopen(req)
print('> Loading data ...')
data = json.loads(res.read())

# store all search results in the temporary JSON file
datapath = 'requests/request_{}{}{}.json'.format(actionDate.split('-')[0],actionDate.split('-')[1],actionDate.split('-')[2])
with open(datapath, 'w') as fw:
    json.dump(data, fw)
with open(datapath) as fr:
    data = json.load(fr)


# split and store JSON search results by month
print('> Searching maps added from {} to {} ...'.format(dateBegin, dateEnd))
searchResult = {}
for month in months:
    maps = [x for x in data if x["date_added"].startswith(month)]
    if maps:
        print()
        print('> Found {} maps added on {}'.format(len(maps), month))
        searchResult[month] = len(maps)
        jsonpath = 'jsons/dateAdded_{}{}.json'.format(month.split('-')[0],month.split('-')[1])
        with open(jsonpath, 'w') as f:
            print('> Saving JSON locally ...')
            jsonObj = json.dumps(maps)
            f.write(jsonObj)

            # create metadata by month
            print('> Preparing Metadata ...')
            full_df = pd.read_json(jsonpath)
            out_df = pd.DataFrame(columns=fieldnames)

            ## extract content from full_df
            out_df['Title'] = full_df['title']
            out_df['Alternative Title'] = full_df['title']
            try:
                out_df['Description'] = full_df['description'] + ' Dimensions: ' + full_df['dimensions']
            except:
                out_df['Description'] = ''

            out_df['Language'] = full_df['language'].str.join('; ')
            out_df['Creator'] = full_df['creator'].str.join('; ')
            # out_df['Publisher'] = full_df['publisher']
            out_df['Keyword'] = full_df['subject'].str.join('|')
            out_df['Date Issued'] = full_df['date_created'].str.join('')

            ## spatial coverage
            try:
                out_df['Spatial Coverage'] = (full_df['city'].str.join('').fillna('') + ', ' + full_df['state'].str.join('')).str.strip(', ')
                

                out_df['Spatial Coverage'] = out_df['Spatial Coverage'].fillna(full_df['country'].str.join(''))    # replace NaN with country
                out_df['Spatial Coverage'] = out_df['Spatial Coverage'].fillna(full_df['continent'].str.join(''))  # replace NaN with continent
                # out_df['Spatial Coverage'] = out_df['Spatial Coverage'].fillna(full_df['region'].str.join(''))     # replace NaN with region
            except:
                out_df['Spatial Coverage'] = ''

            out_df['Information'] = 'https://umedia.lib.umn.edu/item/' + full_df['id']
            out_df['Download'] = 'http://cdm16022.contentdm.oclc.org/utils/getfile/collection/' + full_df['set_spec'] + '/id/' + full_df['parent_id'].astype(str) + '/filename/print/page/download/fparams/forcedownload'
            out_df['Image'] = full_df['thumb_url']
            out_df['Manifest'] = 'https://cdm16022.contentdm.oclc.org/iiif/info/' + full_df['set_spec'] + '/' + full_df['parent_id'].astype(str) + '/manifest.json'
            out_df['Identifier'] = full_df['system_identifier']
            out_df['ID'] = full_df['id']
            out_df['Rights'] = full_df['local_rights']


            ## some hard-code fields
            out_df['Resource Type'] = ''
            out_df['Provider'] = 'University of Minnesota'
            out_df['Code'] = '05d-01'
            out_df['Member Of'] = '05d-01'
            out_df['Status'] = 'Active'
            out_df['Accrual Method'] = 'Blacklight'
            out_df['Access Rights'] = 'Public'
            out_df['Date Accessioned'] = actionDate
            out_df['Resource Class'] = 'Maps'
            out_df['Format'] = 'JPEG'
            out_df['Suppressed'] = 'FALSE'
            out_df['Child Record'] = 'FALSE'

            csvpath = "reports/dateAdded_{}{}.csv".format(month.split('-')[0],month.split('-')[1])
            out_df.to_csv(csvpath, index=False)
            print("> CSV report is created")

print()
print()
print('----------- Search Results -----------')
for m in searchResult:
    print('{} maps added on {}'.format(searchResult[m], m))
