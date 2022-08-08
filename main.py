import requests
import pandas as pd
import json

from bs4 import BeautifulSoup
from urllib.request import urlopen
from datetime import datetime
from tqdm import tqdm

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

        for period in tqdm(periods.values):
            start = period.to_timestamp().strftime('%Y-%m-%d')
            end = period.to_timestamp(how="E").strftime('%Y-%m-%d')
        
            queries = self.query(start, end, interval="hourly").json()
            
            for q in queries:
                hourly_usage[q["date"]] = q["value"]
        

        return hourly_usage
        


class Stats():

    def __init__(self):
        pass

    def hourly_usage_df(self, json):

        df = pd.read_json(json, orient='index')
        df = df.reset_index(level=0)
        df = df.set_axis(['Datetime', 'kWH'], axis=1, inplace=False)

        #print(df['Datetime'].apply(lambda v: isinstance(v, datetime)).sum())
        
        df[['Datetime', 'Timezone']] = df['Datetime'].astype(str).str.rsplit('+', n=1, expand=True)
        df['Datetime'] = pd.to_datetime(df['Datetime'], utc=True)
        df['Timezone'] = pd.to_datetime(df['Timezone'])


        df['Hour'] = df['Datetime'].dt.strftime('%H')
        df['Day'] = df['Datetime'].dt.strftime('%Y-%m-%d')


        hour_df = df.groupby(df['Hour']).sum()
        hour_df["%"] = ((hour_df / hour_df.sum()) * 100).round(decimals=2)

        return df, hour_df





if __name__ == "__main__":

    stats = Stats()

    #api = Contact_Energy_API()
    #api.login()
    #api.query()

    #hourly_usage = api.hourly_power(start="2021-11-17", end="2022-08-05")

    #last_week = api.hourly_power(start="2022-08-01", end="2022-08-06")

    #with open('hourly_usage.json', 'w') as outfile:
    #    json.dump(hourly_usage, outfile, indent = 4)


    df, hour_df = stats.hourly_usage_df('hourly_usage.json')

    current_plan_fixed = 1.059 
    current_plan_cost_per_kWh = 0.2050
    current_plan_discount = 0.98 # 2percent

    good_night_fixed = 1.969
    good_night_cost_per_kwh = 0.2105

    print("Current:")
    print((df.shape[0]/24 * current_plan_fixed  + hour_df["kWH"].sum() * current_plan_cost_per_kWh)) # * current_plan_discount)

    print('Free Hour:')
    print((df.shape[0]/24 * good_night_fixed  + hour_df["kWH"][0:21].sum() * good_night_cost_per_kwh))




