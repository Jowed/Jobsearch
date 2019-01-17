from bs4 import BeautifulSoup
import re
import sys
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

class IndeedSearch:

    def __init__(self, driver_path):
        '''
        Requires a webdriver for setting up Chrome for selenium
        '''
        self.__selenium_setup__(driver_path)

    # Selenium setup
    def __selenium_setup__(self, driver_path):
        browser_options = Options()
        browser_options.headless=True
        browser = webdriver.Chrome(executable_path=driver_path, options=browser_options)
        return browser

    def __getSearchURL__(self, query, location, radius=None, job_type=None, explvl=None):
        '''
        valid parameters:
        radius: [0, 5, 10, 15, 25, 50, 100]
        job_type: [ 'fulltime', 'commission', 'contract', 'internship', 'temporary']
        explvl: ['entry_level', 'mid_level', 'senior_level']
        '''
        url = "http://www.indeed.com/jobs?q=" + query.replace(" ", "+") + \
                "&l=" + location.replace(" ", "+").replace(",", "%2C")
        if(radius != None):
            url += "&radius=" + str(radius)
        if(job_type != None):
            url += "&jt=" + job_type
        if(explvl != None):
            url += "&explvl=" + explvl
        return url

    def __genDivs__(self, soup, limit):
        final = []
        while( soup.find_all("span", {"class" : "pn"})[-1].text.find("Next") >= 0 and len(final) <= limit):
            nextPage = "http://www.indeed.com" + soup.find_all("span", {"class" : "pn"})[-1].parent.attrs["href"]
            try:
                browser.get(nextPage)
            except Exception as e:
                print(e)
            divlist = soup.findAll("div", {"class" : re.compile("jobsearch-SerpJobCard row result clickcard(.*)"),
                                    "data-tn-component" : "organicJob"})
            final += divlist
        return final

    def __getDescription__(self, div, description_type):
        if(description_type == 'full'):
            url = "http://www.indeed.com/" + div.find("a", {"class" : "turnstileLink"}).attrs["href"]
            try:
                browser.get(url)
            except Exception as e:
                print(e)
            soup = BeautifulSoup(browser.page_source, "lxml")
            desc = soup.find("div", {"class" : re.compile("jobsearch-JobComponent-description(.*)")})
            if(desc == None):
                print("Could not find description for " + url)
                raise ValueError
            text = desc.get_text("\n")
            return text
        else:
            return div.find("span", {"class" : "summary"}).get_text(strip=True)

    def __getTitle__(self, div):
        return div.h2.a.attrs["title"]

    def __getCompany__(self, div):
        return div.find("span", {"class" : "company"}).text.strip()

    def __getLastPosted__(self, div):
        return div.find("span", {"class" : "date"}).text

    def __getCity__(self, div):
        return div.find("span", {"class" : "location"}).text.split(',')[0]

    def __getState__(self, div):
        return div.find("span", {"class" : "location"}).text.split(',')[1].strip().split()[0]

    def __getLink__(self, div):
        return "http://www.indeed.com" + div.find("a", {"class" : "turnstileLink"}).attrs["href"]

    def __getGoogleLink__(self, company):
        c = company.replace(' ', '+')
        return "https://www.google.com/search?q=" + c

    def search(self, query, location, radius=None, job_type=None, explvl=None, limit=30, description_type='full'):
        '''
        valid parameters:
        radius: [0, 5, 10, 15, 25, 50, 100]
        job_type: [ 'fulltime', 'commission', 'contract', 'internship', 'temporary']
        explvl: ['entry_level', 'mid_level', 'senior_level']
        description_type: ['summary', 'full']
        '''
        browser = selenium_setup(r"C:\Users\Ryan\Downloads\chromedriver.exe")
        url = self.__getSearchURL__(query, location, radius, job_type, explvl)
        try:
            browser.get(url)
        except Exception as e:
            print(e)
            sys.exit()
        soup = BeautifulSoup(browser.page_source, "lxml")
        divlist = self.__genDivs__(soup, limit)
        
        joblist = []
        for div in divlist:
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
        return joblist
