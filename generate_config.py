# Config file for generate_config.py

# Where to store log files
LOGFILE_DIR = 'logs'

# Start and end dates you want for stats
# (Defaults indicate dates for which GA data is currently available)
STARTDATE = '2010-04-01'
ENDDATE = '2021-04-30'

# The overall Google Analytics metrics you want
# You can find the full list at
# https://developers.google.com/analytics/devguides/reporting/core/dimsmets
PAGE_METRICS = ['ga:pageviews', 'ga:uniquepageviews']

# Where to put downloaded raw GA monthly datasets
GA_OUTPUT_DIR = 'ga_raw_data'

# Our URL list file to process
URL_LIST_FILE = 'url_lists/training_guidestoptips.txt'
#URL_LIST_FILE = 'url_lists/comms_blogposts.txt'
#URL_LIST_FILE = 'url_lists/combined_blogpostsguidestoptips.txt'

# Where to put output reports
REP_OUTPUT_DIR = 'reports'
