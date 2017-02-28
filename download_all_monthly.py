"""
Using Google Analytics V4 API, download all Google Analytics data for each
month between specified start date and end date. Uses Google Analytics V4 API.
"""

import os
import re
import argparse
import pandas as pd
import logging
from sets import Set
from urlparse import urlparse

from dateutil.relativedelta import relativedelta
from datetime import datetime

from apiclient.discovery import build
import httplib2
from oauth2client import client
from oauth2client import file
from oauth2client import tools

from download_config import (LOGFILE_DIR, CLIENT_SECRETS_PATH,
    STARTDATE, ENDDATE, PAGE_METRICS, GA_OUTPUT_DIR)


SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
DISCOVERY_URI = ('https://analyticsreporting.googleapis.com/$discovery/rest')
VIEW_ID = '31084866'  # The SSI software.ac.uk view id

# Set default logging (only set if none already defined)
logfile = 'download-' + datetime.now().strftime('%Y-%m-%d-%H-%M') + '.log'
logging.basicConfig(filename=os.path.join(LOGFILE_DIR, logfile),
                    format='%(asctime)s - %(levelname)s %(funcName)s() - %(message)s')
log = logging.getLogger()
log.setLevel(logging.DEBUG)


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
    log.info("Reading credentials from " + CLIENT_SECRETS_PATH)
    flow = client.flow_from_clientsecrets(
        CLIENT_SECRETS_PATH, scope=SCOPES,
        message=tools.message_if_missing(CLIENT_SECRETS_PATH))

    # Prepare credentials, and authorize HTTP object with them.
    # If the credentials don't exist or are invalid run through the
    # native client flow. The Storage object will ensure that if successful
    # the good credentials will get written back to a file.
    log.info("Storing credentials cache in auth_secret/")
    storage = file.Storage('auth_secret/analyticsreporting.dat')
    credentials = storage.get()
    if credentials is None or credentials.invalid:
        credentials = tools.run_flow(flow, storage, flags)
    http = credentials.authorize(http=httplib2.Http())

    log.info("Building analytics service object")
    analytics = build('analytics', 'v4',
                      http=http, discoveryServiceUrl=DISCOVERY_URI)

    return analytics


def get_report_page(analytics, start_date, end_date, pageSize, pageToken):
    # Use the Analytics Service Object to query the Analytics Reporting API V4

    log.info("Constructing GA JSON request")
    log.info("  From " + str(start_date) + " to " + str(end_date))
    log.info("  Pagesize " + str(pageSize))
    log.info("  Pagetoken " + str(pageToken))

    # The structural body of our GA request
    body = {
        'reportRequests': [{
            'viewId': VIEW_ID,
            'dimensions': [{"name": "ga:pagepath"}],
            'dateRanges': [{
                'startDate': start_date.strftime('%Y-%m-%d'),
                'endDate': end_date.strftime('%Y-%m-%d'),
            }],
            'metrics': [],
            'dimensionFilterClauses': [{
                'filters': [{
                    'operator': 'REGEXP',
                    'dimensionName': 'ga:pagepath',
                    'expressions': ['/'],
                }],
            }],
            'pageSize': pageSize,
            'pageToken': str(pageToken),
        }]
    }

    # Add the metrics we want to capture for each data point
    log.info("Adding metrics to search: " + str(PAGE_METRICS))
    for metric in PAGE_METRICS:
        body['reportRequests'][0]['metrics'].append({'expression': metric})

    log.debug("GA JSON request body: " + str(body))

    return analytics.reports().batchGet(body=body).execute()


def append_to_dataframe(df, response):
    log.info("Received and processing response")
    log.debug(str(response))
    for report in response.get('reports', []):
        columnHeader = report.get('columnHeader', {})
        dimensionHeaders = columnHeader.get('dimensions', [])
        metricHeaders = columnHeader.get('metricHeader', {}).get('metricHeaderEntries', [])
        rows = report.get('data', {}).get('rows', [])

        log.info("Adding data from " + str(len(rows)) + " entries")

        for row in rows:
            dimensions = row.get('dimensions', [])
            dateRangeValues = row.get('metrics', [])

            df_row = []
            for header, dimension in zip(dimensionHeaders, dimensions):
                df_row.append(dimension.encode('utf-8'))

            values = dateRangeValues[0]
            for metricHeader, value in zip(metricHeaders, values.get('values')):
                df_row.append(value.encode('utf-8'))

            df.loc[len(df)] = df_row

    log.info("Appended to dataframe from response")
    log.debug(str(df))

    return df


def get_monthly_ga_data(analytics, columns, startdate, enddate):
    log.info("Obtaining GA raw data for columns " + str(columns))
    log.info("  From " + str(startdate) + " to " + str(enddate))

    df = pd.DataFrame(columns=columns)

    # Iterate through all paginated requests and responses for a monthly
    # period, adding data from each response to a monthlydataframe
    nextPageToken = 0
    while True:
        log.info("Requesting from page token " + str(nextPageToken))
        response = get_report_page(analytics, startdate, enddate,
                                   10000, nextPageToken)
        df = append_to_dataframe(df, response)

        report = response['reports'][0]
        if 'nextPageToken' not in report:
            break

        nextPageToken = report['nextPageToken']

    return df


def main():
    analytics = initialize_analyticsreporting()

    # The entire search date range and column data we want
    startdate = datetime.strptime(STARTDATE, '%Y-%m-%d')
    enddate = datetime.strptime(ENDDATE, '%Y-%m-%d')
    columns = ['ga:pagepath'] + PAGE_METRICS

    # Iterate through date range on a monthly basis,
    # requesting all GA data for that month
    report_startdate = startdate
    while report_startdate <= enddate:
        report_enddate = report_startdate + relativedelta(months=1) - relativedelta(days=1)
        csv_filename = 'ga-report-' + report_startdate.strftime('%Y-%m') + '.csv'

        print "Processing " + report_startdate.strftime('%Y-%m') + "..."

        # Get all GA data for that month, save to separate csv
        print "  Obtaining data from Google Analytics..."
        df = get_monthly_ga_data(analytics, columns,
                                 report_startdate, report_enddate)
        print "  Generating CSV " + csv_filename + "..."
        df.to_csv(os.path.join(GA_OUTPUT_DIR, csv_filename), encoding='utf-8')

        # Calculate our next monthly time period
        report_startdate = report_startdate + relativedelta(months=1)

if __name__ == '__main__':
    main()
