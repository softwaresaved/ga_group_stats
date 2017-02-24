"""
Feasibility test of using Google Analytics V4 API for obtaining summed stats
 for an arbitrary list of URLs held in a file.
"""

import os
import re
import argparse
from urlparse import urlparse

from apiclient.discovery import build
import httplib2
from oauth2client import client
from oauth2client import file
from oauth2client import tools

from config import STARTDATE, ENDDATE, PAGE_METRICS, URL_FILE

SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
DISCOVERY_URI = ('https://analyticsreporting.googleapis.com/$discovery/rest')
CLIENT_SECRETS_PATH = 'auth_secret/client_secrets.json' # Path to client_secrets.json file
VIEW_ID = '31084866'  # The SSI software.ac.uk view id

URL_REGEXP_DATEOPTION = '([0-9]{4}-[0-9]{2}-[0-9]{2}-){0,1}'
URL_REGEXP_QUERYOPTION = '(\?.*){0,1}$'


def initialize_analyticsreporting():
  """Initializes the analyticsreporting service object.

  Returns:
    analytics an authorized analyticsreporting service object.
  """
  # Parse command-line arguments.
  parser = argparse.ArgumentParser(
      formatter_class=argparse.RawDescriptionHelpFormatter,
      parents=[tools.argparser])
  flags = parser.parse_args([])

  # Set up a Flow object to be used if we need to authenticate.
  flow = client.flow_from_clientsecrets(
      CLIENT_SECRETS_PATH, scope=SCOPES,
      message=tools.message_if_missing(CLIENT_SECRETS_PATH))

  # Prepare credentials, and authorize HTTP object with them.
  # If the credentials don't exist or are invalid run through the native client
  # flow. The Storage object will ensure that if successful the good
  # credentials will get written back to a file.
  storage = file.Storage('auth_secret/analyticsreporting.dat')
  credentials = storage.get()
  if credentials is None or credentials.invalid:
    credentials = tools.run_flow(flow, storage, flags)
  http = credentials.authorize(http=httplib2.Http())

  # Build the service object.
  analytics = build('analytics', 'v4', http=http, discoveryServiceUrl=DISCOVERY_URI)

  return analytics

def get_report(analytics):
  # Use the Analytics Service Object to query the Analytics Reporting API V4

  # The structural body of our GA request
  body={
    'reportRequests': [{
      'viewId': VIEW_ID,
      'dateRanges': [{'startDate': STARTDATE, 'endDate': ENDDATE}],
      'metrics': [],
      'dimensionFilterClauses': [{
        'filters': []
      }]
    }]
  }

  # Add each url listed in URL_FILE to our JSON 'filters'
  # element above. e.g. pages are included in stats if found
  # through at least one of these multiple filters
  file = open(URL_FILE, 'r')
  for url in file:
    if url[0] == '#':
        continue

    # Extract the path and page from the URL
    url_path = urlparse(url).path
    path, page = os.path.split(url_path.strip())

    # Remove any fixed date already prefixed to page name, to increase chances
    # we'll find any duplicate content (with perhaps other fixed date prefixes)
    page = re.sub('^' + URL_REGEXP_DATEOPTION, '', page)

    # Our regular expression to find our page, with an optional date prefix in page
    # name and optional HTTP get query, so we can group stats for all aliases/copies
    # of same actual content
    url_regexp = '^' + path + '/' + URL_REGEXP_DATEOPTION + page + URL_REGEXP_QUERYOPTION
    body['reportRequests'][0]['dimensionFilterClauses'][0]['filters'].append({
      'operator': "REGEXP",
      'dimensionName': 'ga:pagePath',
      'expressions': [ url_regexp ]
    })
  file.close()

  # Add each metric for which we want to provide an overall calculation
  for metric in PAGE_METRICS:
    body['reportRequests'][0]['metrics'].append({'expression': metric})

  return analytics.reports().batchGet(body=body).execute()


def print_response(response):
  """Parses and prints the Analytics Reporting API V4 response"""

  for report in response.get('reports', []):
    columnHeader = report.get('columnHeader', {})
    dimensionHeaders = columnHeader.get('dimensions', [])
    metricHeaders = columnHeader.get('metricHeader', {}).get('metricHeaderEntries', [])
    rows = report.get('data', {}).get('rows', [])

    for row in rows:
      dimensions = row.get('dimensions', [])
      dateRangeValues = row.get('metrics', [])

      for header, dimension in zip(dimensionHeaders, dimensions):
        print header + ': ' + dimension

      values = dateRangeValues[0]
      for metricHeader, value in zip(metricHeaders, values.get('values')):
        print metricHeader.get('name') + ': ' + value


def main():

  analytics = initialize_analyticsreporting()
  response = get_report(analytics)
  print_response(response)

if __name__ == '__main__':
  main()
