# Config file for download_all_monthly.py

# Start and end dates you want for stats
STARTDATE = '2017-01-01'
ENDDATE = '2017-02-28'

# The overall Google Analytics metrics you want
# You can find the full list at
# https://developers.google.com/analytics/devguides/reporting/core/dimsmets
PAGE_METRICS = ['ga:pageviews', 'ga:uniquepageviews']

# Where to put downloaded raw GA monthly datasets
OUTPUT_DIR = 'ga_raw_data'
