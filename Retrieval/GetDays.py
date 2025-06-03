# libraies
import yfinance as yf
import pandas as pd
from yahooquery import search
import os
from datetime import datetime
import numpy as np 

# cleaning of the stock of merging and getting close open etc over years
class DayStockData:

    # intilaize variables
    def __init__(self):
        
        # Full datframe of all data
        self.df = None

        # abbrivation of stock
        self.name_abb = None

        # stock name
        self.name = None

        # start date
        self.start = None
        
        # Path to save and search for csv
        self.path = None

    # if file is already cleaned and you want to just add columns or fix data comparsion it will update
    def get(self, stock):

        self.name = stock

        # path to csv
        self.path = os.path.join(stock, f"{stock} day to day.csv")

        if not os.path.exists(self.path):

            self.get_start_end_date()

            self.get_days()


    # obatins start date from the quarterly reports
    def get_start_end_date(self):

        # df from quarterly
        self.df = pd.read_csv(f'{self.name}/{self.name}_combined_quarterly.csv')
        
        # get start
        self.start = self.df.iloc[0]['Date']

    # gets abbrivation bc using stock search up requires abbrivation
    def get_abbr(self):

        # search up stock for abbrivation 
        results = search(self.name)

        # set abbrivation
        self.name_abb = results['quotes'][0]['symbol']
        
        # print marker for check
        print(self.name_abb )

    # gets days of stock over a period
    def get_days(self):

        try:
            # First try with self.name
            self.days = yf.download(self.name, start=self.start,
                                    end=datetime.today().strftime('%Y-%m-%d'),
                                    auto_adjust=True, progress=False)
            if self.days.empty:
                raise ValueError("Empty data for self.name")

        except Exception as e:

            self.get_abbr()

            print(f"⚠️ Failed to download using self.name ({self.name}): {e}")
            print(f"➡️ Trying fallback ticker: {self.name_abb}")
            

            # Try with abbreviation
            self.days = yf.download(self.name_abb, start=self.start,
                                    end=datetime.today().strftime('%Y-%m-%d'),
                                    auto_adjust=True, progress=False)
            if self.days.empty:
                raise ValueError(f"❌ Failed to download data for both {self.name} and {self.name_abb}")

        print("✅ Download successful!")

        self.days.columns = self.days.columns.droplevel('Ticker')

        self.days.reset_index(inplace=True)

        # Then save
        self.days.to_csv(self.path, index=False)
