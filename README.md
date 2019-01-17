# Jobsearch module
A python library to scrape for job posts

## IndeedSearch
    search(query, location[, radius[, job_type[, explevel[, limit[, description_type]]]]])

    Retrieves and returns results from a search on Indeed. Limit the amount of results with the limit parameter.
    Output specifies whether to print status updates. Changing description type to 'summary' will result in
    faster runtimes.

    valid parameters:
    radius: [0, 5, 10, 15, 25, 50, 100] (in miles)
    job_type: [ 'fulltime', 'commission', 'contract', 'internship', 'temporary']
    explvl: ['entry_level', 'mid_level', 'senior_level']
    description_type: ['summary', 'full']
    sort: ['relevence', 'date']
<h2>Usage:</h2>
<p>
  from Jobsearch import IndeedSearch
  <br />
  driver_path = "C:/User/Downloads/chromedriver.exe"
  <br />
  s = IndeedSearch(driver_path)
  <br />
  jobs = s.search("entry level developer", "San Francisco", limit=3)
</p>
