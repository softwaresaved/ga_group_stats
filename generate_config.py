# Config file for generate_config.py

# Where to store log files
LOGFILE_DIR = 'logs'

# Start and end dates you want for stats
STARTDATE = '2015-06-01'
ENDDATE = '2017-02-28'

# The overall Google Analytics metrics you want
# You can find the full list at
# https://developers.google.com/analytics/devguides/reporting/core/dimsmets
PAGE_METRICS = ['ga:pageviews', 'ga:uniquepageviews']

# Where to put downloaded raw GA monthly datasets
GA_OUTPUT_DIR = 'ga_raw_data'

# Our URL list file to process
#URL_LIST_FILE = 'url_lists/training_guidesandtools.txt'
URL_LIST_FILE = 'url_lists/community.txt'
#URL_LIST_FILE = 'url_lists/policy_analysis.txt'
#URL_LIST_FILE = 'url_lists/policy_rse.txt'
#URL_LIST_FILE = 'url_lists/rsg_website.txt'

# Where to put output reports
REP_OUTPUT_DIR = 'reports'
