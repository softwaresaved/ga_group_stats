# Config file for download_all_monthly.py

# Where our downloaded credentials are stored
CLIENT_SECRETS_PATH = 'auth_secret/client_secrets.json'

# Where to store log files
LOGFILE_DIR = 'logs'

# Start and end dates you want for stats
# (Defaults indicate dates for which GA data is currently available)
STARTDATE = '2010-04-01'
ENDDATE = '2021-08-31'

# The overall Google Analytics metrics you want
# You can find the full list at
# https://developers.google.com/analytics/devguides/reporting/core/dimsmets
PAGE_METRICS = ['ga:pageviews', 'ga:uniquepageviews']

# Where to put downloaded raw GA monthly datasets
GA_OUTPUT_DIR = 'ga_raw_data'
