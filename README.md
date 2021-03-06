# Google Analytics (GA) website stats for a group of URLs

Given a set of URLs in a text file, a list of GA metrics to capture,
and a start and end date, this tool provides the following website
statistic reports in CSV format for the given time period for those URLs:

* An overall summary of summed metrics per month
* An overall, sorted summary of metrics per page, including a list of
URLs per page that are just variants of the same URL - i.e. they are the
same page and should be counted as such
* Individual monthly reports of metrics (and page variants) per page

It uses a pre-downloaded set of monthly GA data for the entire website,
which currently exists for the period April 2010 - February 2020. Thus,
reports can only be generated within (or equal to) this current time
period unless further monthly data sets are downloaded. The default
time period for the script is from the start of SSI2 project to February
2020.


## Generating reports

### How it's put together

* [url_lists/](url_lists) - Directory of files each holding sets of pages to process,
one URL per line
* [generate_config.py](generate_config.py) - The configuration file where you specify the
start and end dates for the analysis period, the metrics you wish to
capture, and the specific file of URLs to process held in `url_lists/`
* [generate_group_stats.py](generate_group_stats.py) - The script which takes the configuration in
`generate_config.py` and produces the reports
* [reports/](reports) - Directory that holds the reports generated by
`generate_group_stats.py`, with each subdirectory holding results for running
the tool over a distinct URL list and date range
* [ga_raw_data/](ga_raw_data) - Directory that holds the pre-downloaded GA data for
entire website, used by `generate_group_stats.py`
* [logs/](logs) - Directory which holds log files for processing runs, named
`generate-<date>.log`


### Requirements

* Python 3 (tested on Python 3.6.0)
* Python libraries (installable via `pip install -r requirements.txt` -
see `requirements.txt` for specific details of versions used during
development and testing, others may work):
    * pandas
    * numpy


### Configuration

Edit the `generate_config.py` file and edit the following parameters:

* `STARTDATE`, `ENDDATE` - The start and end dates for the period for
which you wish to generate reports, in `YYYY-MM-DD` format. The defaults
are for the SSI2 project timeframe, from June 1 2015 to February 28 2017
* `PAGE_METRICS` - The metrics you wish to capture in reports as CSV columns.
The ones supported at the moment are overall page views `ga:pageviews` and
unique page views `ga:uniquepageviews`, which are set as defaults. You can
find others at [https://developers.google.com/analytics/devguides/reporting/core/dimsmets](https://developers.google.com/analytics/devguides/reporting/core/dimsmets),
so if you'd like others to be added raise an [issue](https://github.com/softwaresaved/ga_group_stats/issues)
on this repository. Note that generated reports will be sorted by the
first metric specified
* `URL_LIST_FILE` - The file of URLs you wish to generate reports
for within the time period, held in the `url_lists/` directory,
with a single URL per line. The default file given is for a small
test set


### How searching works, and specifying the URLs to check

For each URL you wish to process, add a line to a file specified
by `URL_LIST_FILE` in `generate_config.py`.

The tool is designed to cater for the various idiosyncracies in how
GA reports page hits multiple times for the same actual content, and
the different page naming conventions that have been historically
supported across our website.

Therefore, when it comes to searching the GA data, a number of
different permutations of the same URL are supported, which seem
to cater for 99% of cases. These are:

- Those that are the exact URL, e.g. `http://software.ac.uk/blog/whats-wrong-computer-scientists`
- Those that have a date prefix, e.g. `http://software.ac.uk/blog/2013-10-31-whats-wrong-computer-scientists`
- Those that have a querystring suffix, e.g. `http://software.ac.uk/blog/2013-10-31-whats-wrong-computer-scientists?mpw=`
- Those without a protocol and domain name prefix, e.g. `/blog/whats-wrong-computer-scientists`
- Those with an alias located elsewhere that have the same page name, e.g. `/whats-wrong-computer-scientists`
- Combinations of these

Essentially, the URLs which are supplied are 'shortened' to their
core path and page 'meaning', e.g. to `whats-wrong-computer-scientists`,
to be used for searching. This helps to ensure that such variants of this
core page can be found, so that stats data for a given page isn't missed.
Any duplicate 'core pages' in the URL list file are ignored - since you
wouldn't want to count the stats twice for the same content.

It's also been implemented to ensure that other page URLs that contain that
core page but have different content e.g. `/blog/whats-wrong-computer-scientists-part-ii`,
are not counted. All other page hits which contain the core page - but are
registered in GA as page hits regardless - shouldn't be counted are ignored
in statistics calculations, e.g. those with prefixes `404`, `/search?`, etc.


### Running the report generation tool

Simply type `python generate_group_stats.py` at the command line. A
summary of progress for processing and generating reports per month,
and overall, will be displayed.


### Examining the reports

In the `reports/` directory, you should see a subdirectory named after
your `URL_LIST_FILE` which holds the generated reports:

* A further subdirectory called `monthly_reports`, which holds a
number of Comma-Separated Value (CSV) reports with filenames matching
`ga-report-<url-file>-<year-month>.csv`, each containing summaries across
all core pages for each given metric
* A `ga-summary-monthly-<url-file>-<time-period>.csv` CSV report which contains
a monthly breakdown over the time period for the given metrics
* A `ga-summary-yearly-<url-file>-<time-period>.csv` CSV report which contains
a yearly breakdown over the time period for the given metrics
* A `ga-complete-<url-file>-<time-period>.csv` CSV report which contains
an overall breakdown, per core page, for the given metrics

Note that each report will be sorted by the first metric specified
in `PAGE_METRICS` given in `generate_config.py`, and reports generated
will overwrite any existing ones.


## Downloading GA stats data

### How it's put together

Given the data has already been downloaded and stored in this repository,
there is no need to use this capability unless you wish to expand the set
of overall monthly stats it can use:

* [auth_secret/](auth_secret) - Contains `client_secrets.json` file to hold credential
to authenticate with GA. See [https://developers.google.com/analytics/devguides/reporting/core/v4/quickstart/service-py](https://developers.google.com/analytics/devguides/reporting/core/v4/quickstart/service-py)
for details on how to obtain a usable credential based on your Google
account, using the Google Developers Console. Your Google account will
need to be first authorised within GA by a GA site administrator
* [download_config.py](download_config.py) - The configuration file to specify the start and
end dates for obtaining entire website statistics from GA, the metrics
to capture, and the Google credential to use to authenticate with GA
* [download_all_config.py](download_all_config.py) - The script which takes the configuration in
`download_config.py` and downloads the monthly website statistics from GA
* [ga_raw_data/](ga_raw_data) - Directory which will hold the downoaded monthly
statistics
* [logs/](logs) - Directory which holds log files for processing runs, named
`download-<date>.log`

### Requirements

There's no need to satisfy these requirements if you only want to
generate reports. It's only needed if you want to expand the existing
GA monthly data sets beyond the currently stored period data (see above).

In addition to the requirements for generating reports, these additional
requirements need to be satisfied:

* Python libraries
    * google-api-python-client (only needed for downloading statistics)
* Google account authorised with GA site administrator
* Generated and downloaded GA JSON credential

See [https://developers.google.com/analytics/devguides/reporting/core/v4/quickstart/service-py](https://developers.google.com/analytics/devguides/reporting/core/v4/quickstart/service-py)
for more details on generating a GA JSON credential.

### Configuration

Edit the `generate_config.py` file and edit the following parameters:

* `CLIENT_SECRETS_PATH` - The path to the GA JSON credential.
* `STARTDATE`, `ENDDATE` - The start and end dates for the period for
which you wish to download GA statistics, in `YYYY-MM-DD` format. The defaults
are for the entire lifecycle of SSI.
* `PAGE_METRICS` - The metrics you wish to capture in reports as CSV columns.
The ones supported at the moment are overall page views `ga:pageviews` and
unique page views `ga:uniquepageviews`, which are set as defaults. You can
find others at [https://developers.google.com/analytics/devguides/reporting/core/dimsmets](https://developers.google.com/analytics/devguides/reporting/core/dimsmets),
so if you'd like others to be added raise an [issue](https://github.com/softwaresaved/ga_group_stats/issues)
on this repository. Only the metrics captured during this process can be used
in report generation (see above).

### Running the download tool

Simply type `python download_all_monthly.py` at the command line. A
summary of progress for processing and generating reports per month,
and overall, will be displayed. If this is the first time running this
command, you will be redirected to a Google login page on your browser
to authenticate with the service. When this happens, use the account
from which you generated the `client_secrets.json` credential file.
