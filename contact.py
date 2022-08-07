import requests
import pandas as pd
import json

from bs4 import BeautifulSoup
from urllib.request import urlopen

import creds

login_url = 'https://contact.co.nz/contact/account/signin'
base_url = 'https://api.contact-digital-prod.net'
API_TOKEN = "kbIthASA7e1M3NmpMdGrn2Yqe0yHcCjL4QNPSUij" # This is public



class Contact_Energy_API():
    
    def __init__(self):
        
        self.session = requests.session() 
        self.headers = {"x-api-key": API_TOKEN}
        print("Session Started...")


    def login(self):
        
        login_request = self.session.post(login_url, data=creds.payload)

        if login_request.json()["IsSuccessful"]:
            print("Login Successful")
        else:
            print("Login Failed")

        self.auth_token = str(login_request.json()['Data']['Token'])
        self.headers["authorization"] =  self.auth_token


    def query(self, start="2022-03-01", end="2022-08-31", interval="monthly"):
        """ start / end -> yyyy-mm-dd """

        data_query = f'https://api.contact-digital-prod.net/usage/{creds.ID}?interval={interval}&from={start}&to={end}'

        return self.session.post(data_query, headers=self.headers)

    
    def hourly_power(self, start="2022-03-01", end="2022-03-08"):
        """ API limits to 7 days for hourly (says it does)
            but it actually only returns data for a day...
         """
        hourly_usage = {}

        periods = pd.period_range(start=start,
                                  end=end,
                                  freq='D')

        for period in periods.values:
            start = period.to_timestamp().strftime('%Y-%m-%d')
            end = period.to_timestamp(how="E").strftime('%Y-%m-%d')
        
            q = self.query(start, end, interval="hourly").json()

            hourly_usage[f'{q["date"]}'] = f'{q["value"]}'

        return json.dumps(hourly_usage, indent = 4)  
        


class Visualizer():

    def __init__(self):
        pass




if __name__ == "__main__":

    api = Contact_Energy_API()
    api.login()
    api.query()

    hourly_usage = api.hourly_power()






s = requests.session() 
login = s.post(login_url, data=creds.payload)
auth_token = str(login.json()['Data']['Token'])


#soup = BeautifulSoup







#s = requests.session()
#r = s.options('https://myaccount-api.genesisenergy.co.nz/api/authorize', data={'username':'MrX','password':'123'})
#print(r.text)







quit()

url_to_scrape = "https://myaccount.contact.co.nz/usage"
request_page = urlopen(url_to_scrape)
page_html = request_page.read()
request_page.close()

soup = BeautifulSoup(page_html, 'html.parser')

print(soup.prettify())



