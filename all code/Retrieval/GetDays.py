# Libraries
import yfinance as yf
import pandas as pd
from yahooquery import search
import os
from datetime import datetime
import numpy as np

# Class to get and store daily stock data
class DayStockData:

    # Constructor to initialize the object
    def __init__(self):
        self.df = None  # DataFrame to hold quarterly data
        self.name_abb = None  # Abbreviation (ticker) of the stock
        self.name = None  # Full name of the stock
        self.start = None  # Start date for historical data
        self.path = None  # Path to save daily CSV

    # Main method to handle daily data download
    def get(self, stock):
        self.name = stock
        self.path = os.path.join("stock", stock, f"{stock} day to day.csv")

        # ✅ Ensure the folder exists
        os.makedirs(os.path.dirname(self.path), exist_ok=True)

        # Only download if file doesn't already exist
        if not os.path.exists(self.path):
            print(f"📥 Starting download for {stock}...")
            self.get_start_end_date()  # Get the start date from quarterly CSV
            self.get_days()  # Download daily data

    # Gets the start date from the first row of the quarterly file
    def get_start_end_date(self):
        self.df = pd.read_csv(f'stock/{self.name}/{self.name}_combined_quarterly.csv')
        self.start = self.df.iloc[0]['Date']  # Start from the earliest quarterly entry

    # Uses Yahoo Query API to resolve stock ticker symbol
    def get_abbr(self):
        results = search(self.name)
        self.name_abb = results['quotes'][0]['symbol']
        print(f"🔁 Resolved ticker for {self.name}: {self.name_abb}")

    # Downloads the daily stock data using yfinance
    def get_days(self):
        try:
            # First attempt using full stock name
            self.days = yf.download(
                self.name,
                start=self.start,
                end=datetime.today().strftime('%Y-%m-%d'),
                auto_adjust=True,
                progress=False
            )

            # Raise error if nothing is returned
            if self.days.empty:
                raise ValueError("Empty data for self.name")

        except Exception as e:
            # On failure, try resolving ticker abbreviation
            try:
                self.get_abbr()
            except Exception as abbr_error:
                raise RuntimeError(
                    f"❌ Failed to get abbreviation for '{self.name}' due to: {abbr_error}\n"
                    f"Original download error: {e}"
                )

            print(f"⚠️ Failed to download using '{self.name}': {e}")
            print(f"➡️ Trying fallback ticker: {self.name_abb}")

            # Retry download using resolved ticker symbol
            self.days = yf.download(
                self.name_abb,
                start=self.start,
                end=datetime.today().strftime('%Y-%m-%d'),
                auto_adjust=True,
                progress=False
            )

            if self.days.empty:
                raise ValueError(f"❌ Failed to download data for both '{self.name}' and '{self.name_abb}'")

        # ✅ If multi-level columns, flatten
        if 'Ticker' in self.days.columns.names:
            self.days.columns = self.days.columns.droplevel('Ticker')

        # Reset index to get 'Date' as a column
        self.days.reset_index(inplace=True)

        # ✅ Save to local CSV
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        self.days.to_csv(self.path, index=False)
        print(f"✅ Saved day-to-day data to: {self.path}")
