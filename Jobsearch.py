from bs4 import BeautifulSoup
import re
import sys
import time
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

class IndeedSearch:

    def __init__(self, driver_path):
        '''
        Requires a webdriver path for setting up Chrome for selenium
        '''
        self.__selenium_setup__(driver_path)

    def __selenium_setup__(self, driver_path):
        '''
        Sets up browser options
        '''
        browser_options = Options()
        browser_options.headless=True
        self.browser = webdriver.Chrome(executable_path=driver_path, options=browser_options)
        self.browser.implicitly_wait(3)

    def __getSearchURL__(self, query, location, radius=None, job_type=None, explvl=None, sort=None):
        '''
        Builds URL based on settings
        '''
        url = "http://www.indeed.com/jobs?q=" + query.replace(" ", "+") + \
                "&l=" + location.replace(" ", "+").replace(",", "%2C")
        if(radius != None):
            url += "&radius=" + str(radius)
        if(job_type != None):
            url += "&jt=" + job_type
        if(explvl != None):
            url += "&explvl=" + explvl
        if(sort != None):
            url += "&sort=" + sort
        return url

    def __genDivs__(self, soup, limit, output):
        '''
        Generates the divs for parsing.
        '''
        final = []
        if( soup.find_all("span", {"class" : "pn"}) != None and len(soup.find_all("span", {"class" : "pn"})) != 0 ):
            while( soup.find_all("span", {"class" : "pn"})[-1].text.find("Next") >= 0 and len(final) <= limit):
                nextPage = "http://www.indeed.com" + soup.find_all("span", {"class" : "pn"})[-1].parent.attrs["href"]
                try:
                    self.browser.get(nextPage)
                except Exception as e:
                    print(e)
                soup = BeautifulSoup(self.browser.page_source, "lxml")
                divlist = soup.findAll("div", {"class" : re.compile("jobsearch-SerpJobCard row result clickcard(.*)"),
                                        "data-tn-component" : "organicJob"})
                final += divlist
        else:
            soup = BeautifulSoup(self.browser.page_source, "lxml")
            divlist = soup.findAll("div", {"class" : re.compile("jobsearch-SerpJobCard row result clickcard(.*)"),
                                    "data-tn-component" : "organicJob"})
            final = divlist


        if(output):
            print("Retrieved divs")
        return final

    def __getDescription__(self, div, description_type):
        '''
        Retrieves the description from the div
        '''
        if(description_type == 'full'):
            url = "http://www.indeed.com/" + div.find("a", {"class" : "turnstileLink"}).attrs["href"]
            try:
                self.browser.get(url)
            except Exception as e:
                print(e)
            soup = BeautifulSoup(self.browser.page_source, "lxml")
            desc = soup.find("div", {"class" : re.compile("jobsearch-JobComponent-description(.*)")})
            if(desc == None):
                print("Could not find description for " + url)
                raise ValueError
            text = desc.get_text("\n")
            return text
        else:
            return div.find("span", {"class" : "summary"}).get_text("\n", strip=True)

    def __getTitle__(self, div):
        '''
        Retrieves the title from the div
        '''
        return div.h2.a.attrs["title"]

    def __getCompany__(self, div):
        '''
        Retrieves the company from the div
        '''
        return div.find("span", {"class" : "company"}).text.strip()

    def __getLastPosted__(self, div):
        '''
        Retrieves how long ago posted from the div
        '''
        return div.find("span", {"class" : "date"}).text

    def __getCity__(self, div):
        '''
        Retrieves the city from the div
        '''
        return div.find("span", {"class" : "location"}).text.split(',')[0]

    def __getState__(self, div):
        '''
        Retrieves the state from the div
        '''
        return div.find("span", {"class" : "location"}).text.split(',')[1].strip().split()[0]

    def __getLink__(self, div):
        '''
        Retrieves the post link from the div
        '''
        return "http://www.indeed.com" + div.find("a", {"class" : "turnstileLink"}).attrs["href"]

    def __getGoogleLink__(self, company):
        '''
        Generates a link to Google search for the company
        '''
        c = company.replace(' ', '+')
        return "https://www.google.com/search?q=" + c

    def search(self, query, location, radius=None, job_type=None, explvl=None, \
                limit=30, description_type='full', sort='relevence', output=True):
        '''
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
        '''
        url = self.__getSearchURL__(query, location, radius, job_type, explvl, sort)
        try:
            self.browser.get(url)
        except Exception as e:
            print(e)
            sys.exit()
        soup = BeautifulSoup(self.browser.page_source, "lxml")
        divlist = self.__genDivs__(soup, limit, output)
        
        joblist = []
        for i, div in enumerate(divlist):
            time.sleep(.001) # sleep so Indeed doesn't lock you out
            title = self.__getTitle__(div)
            company = self.__getCompany__(div)
            timeago = self.__getLastPosted__(div)
            city = self.__getCity__(div)
            state = self.__getState__(div)
            description = self.__getDescription__(div, description_type)
            link = self.__getLink__(div)
            googleLink = self.__getGoogleLink__(company)
            joblist.append({'title' : title,
                            'company' : company,
                            'description' : description,
                            'posted' : timeago,
                            'link' : link,
                            'googleLink' : googleLink,
                            'city' : city,
                            'state' : state})
            if(i % 50 == 0 and i != 0 and output):
                print("Retrieved", i, "job posts")

        print("Retrieved", len(joblist), "job posts")
        return joblist
