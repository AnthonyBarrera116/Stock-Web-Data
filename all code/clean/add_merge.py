""" 
RiskAnalyzer

This module defines the RiskAnalyzer class which loads daily and quarterly stock data,
merges them by date, and generates engineered features for financial risk assessment
and investment decision-making. It outputs two CSV files per stock:

1. A full merged dataset (`<stock>.csv`) with all original and new features.
2. A risk-only dataset (`<stock> risk only.csv`) with only the engineered columns.

Feature Definitions:
- Date: Trading day
- Year: Calendar year
- Day: Day of year (1-365/366)
- daily_return: % change from previous close
- volatility_10d: Std dev of daily returns over 10 days
- volatility_30d: Std dev of daily returns over 30 days
- rolling_max: Cumulative max of Close price
- drawdown: Drop from rolling max
- max_drawdown: Worst drawdown in past 30 days
- quick_ratio: (Cash + Receivables) / Current Liabilities
- debt_ratio: Total Liabilities / Total Assets
- cash_burn: Monthly cash usage based on operations
- months_of_cash: Cash runway based on burn rate
- eps_change_qoq: EPS % change from last quarter
- margin_trend: 3-quarter moving avg of net profit margin
- rd_intensity: R&D Expenses / Revenue
- earnings_quality: Non-cash items / Net income
- risk_score: Composite risk score from scaled metrics
- risk_level_code: Risk category (0=Low, 1=Med, 2=High)
- news_score: Synthetic sentiment from future returns
- gap_flag: 1 if daily return >5% gap, else 0
- momentum_5d: 5-day price momentum
- price_range: High - Low for the day
- intraday_volatility: (High - Low) / Open
- close_to_open: (Close - Open) / Open
- rolling_avg_close_10: 10-day moving avg of Close
- rolling_std_close_10: 10-day rolling std dev of Close
- rolling_return_10d: 10-day % return
- future_return_20d: 20-day forward % return
- long_term_signal: 1 = Buy, 0 = Wait, -1 = Sell
"""

# Imports core libraries for data analysis and modeling
import pandas as pd  # For handling tabular stock and financial data
import numpy as np  # For numerical calculations and rolling stats
from sklearn.preprocessing import MinMaxScaler  # For normalizing features for risk scoring
import os  # For file path manipulation and saving
""# ... (Top-level docstring and imports remain unchanged)

# Main class to handle risk and feature engineering
class RiskAnalyzer:
    def __init__(self, df=None):
        self.df = df  # Quarterly data (financial statements and metrics)
        self.days = None  # Daily stock data (Open, High, Low, Close, Volume)
        self.p = 0  # Internal processing flag

    # Merges quarterly financial data into daily data based on date proximity
    def merge_quarterly_day_to_day(self):
        if isinstance(self.days.columns, pd.MultiIndex):  # Flatten MultiIndex columns if present
            self.days.columns = [col[0] for col in self.days.columns.values]

        self.df = self.df.drop_duplicates(subset='Date').sort_values('Date')  # Clean and sort quarterly
        self.days = self.days.drop_duplicates(subset='Date').sort_values('Date')  # Clean and sort daily

        emp_df = None  # Will temporarily hold employee count if needed
        if 'Employees' in self.df.columns:  # If employee data exists
            emp_df = self.df[['Date', 'Employees']].drop_duplicates().sort_values('Date')
            self.df = self.df.drop(columns=['Employees'])  # Drop it from df to merge later

        # Merge quarterly data into daily data backward in time
        merged = pd.merge_asof(
            self.days.sort_values('Date'),
            self.df.sort_values('Date'),
            on='Date',
            direction='backward'
        )

        # If employee data was separated, merge it back
        if emp_df is not None:
            merged = pd.merge_asof(
                merged.sort_values('Date'),
                emp_df.sort_values('Date'),
                on='Date',
                direction='backward'
            )

        self.df = merged  # Set final merged dataset

    # Main method to calculate and save all features for a stock
    def compute_all(self, s=None):
        if s is not None:
            day_path = os.path.join("stock", s, f"{s} day to day.csv")  # Path to daily CSV
            fin_path = os.path.join("stock", s, f"{s}_combined_quarterly.csv")  # Path to quarterly CSV
            self.days = pd.read_csv(day_path)  # Load daily data
            self.df = pd.read_csv(fin_path)  # Load quarterly data
            self.days['Date'] = pd.to_datetime(self.days['Date'], errors='coerce')
            self.df['Date'] = pd.to_datetime(self.df['Date'], errors='coerce')
            self.merge_quarterly_day_to_day()  # Merge daily and quarterly
        else:
            self.p = 1  # Only process if df already loaded manually

        original_cols = set(self.df.columns)  # Save original feature columns

        # Compute engineered features step by step
        self.compute_volatility()  # Price-based volatility metrics
        self.compute_quick_ratio()  # Quick liquidity metric
        self.compute_debt_ratio()  # Leverage metric
        self.compute_cash_burn()  # Monthly burn rate from ops
        self.compute_months_of_cash()  # Runway estimate
        self.compute_eps_change()  # EPS growth
        self.compute_margin_trend()  # Profit margin trend
        self.compute_rd_intensity()  # R&D expense as revenue share
        self.compute_earnings_quality()  # Non-cash item reliance
        self.compute_composite_risk()  # Combined scaled risk score
        self.add_news_column()  # Pseudo-sentiment via returns
        self.compute_long_term_features()  # Trends and volatility
        self.compute_long_term_signal()  # Buy/Sell signal

        self.df.fillna(0, inplace=True)  # Clean all missing data

        if s is not None:
            if 'Date' in self.df.columns and np.issubdtype(self.df['Date'].dtype, np.datetime64):
                self.df['Year'] = self.df['Date'].dt.year
                self.df['Month'] = self.df['Date'].dt.month
                self.df['Day'] = self.df['Date'].dt.day
                front = ['Year', 'Month', 'Day']
                rest = [col for col in self.df.columns if col not in front + ['Date']]
                self.df = self.df[front + rest]  # Reorder
                self.df.drop(columns='Date', inplace=True, errors='ignore')

            # Save full processed dataset
            full_output_path = os.path.join("stock", s, f"{s}.csv")
            self.df.to_csv(full_output_path, index=False)

            # Save dataset with only new engineered features
            new_cols = [col for col in self.df.columns if col not in original_cols and col not in ['Date']]
            date_parts = [col for col in ['Year', 'Month', 'Day'] if col in self.df.columns]
            risk_only_df = self.df[date_parts + new_cols]
            risk_output_path = os.path.join("stock", s, f"{s} risk only.csv")
            risk_only_df.to_csv(risk_output_path, index=False)
        else:
            return self.df

    # Calculates daily return, short/long-term volatility, and drawdown
    def compute_volatility(self):
        df = self.df
        df['daily_return'] = df['Close'].pct_change()
        df['volatility_10d'] = df['daily_return'].rolling(window=10).std()
        df['volatility_30d'] = df['daily_return'].rolling(window=30).std()
        df['rolling_max'] = df['Close'].cummax()
        df['drawdown'] = df['Close'] / df['rolling_max'] - 1
        df['max_drawdown'] = df['drawdown'].rolling(window=30).min()

    # Computes liquidity: cash + receivables over current liabilities
    def compute_quick_ratio(self):
        self.df['quick_ratio'] = (
            self.df['balance_sheet_Cash On Hand'] + self.df['balance_sheet_Receivables']
        ) / self.df['balance_sheet_Total Current Liabilities']

    # Computes financial leverage
    def compute_debt_ratio(self):
        self.df['debt_ratio'] = self.df['balance_sheet_Total Liabilities'] / self.df['balance_sheet_Total Assets']

    # Calculates monthly cash burn from operating cash flow
    def compute_cash_burn(self):
        self.df['cash_burn'] = -self.df['cash_flow_statement_Cash Flow From Operating Activities']

    # Estimates how many months of operations cash can cover
    def compute_months_of_cash(self):
        self.df['months_of_cash'] = self.df['balance_sheet_Cash On Hand'] / (self.df['cash_burn'] / 12)

    # Computes EPS growth vs last quarter
    def compute_eps_change(self):
        self.df['eps_change_qoq'] = self.df['financials_EPS - Earnings Per Share'].pct_change()

    # Computes average net margin over last 3 quarters
    def compute_margin_trend(self):
        self.df['margin_trend'] = self.df['key_financial_ratios_Net Profit Margin'].rolling(window=3).mean()

    # R&D expense as a share of total revenue
    def compute_rd_intensity(self):
        self.df['rd_intensity'] = self.df['financials_Research And Development Expenses'] / self.df['financials_Revenue']

    # Compares non-cash activity to reported net income
    def compute_earnings_quality(self):
        df = self.df
        df['earnings_quality'] = df['cash_flow_statement_Total Non-Cash Items'] / df['cash_flow_statement_Net Income/Loss']

    # Combines several risk factors into a single normalized score
    def compute_composite_risk(self, p=0):
        risk_cols = ['volatility_30d', 'debt_ratio', 'cash_burn', 'eps_change_qoq', 'earnings_quality']
        risk_factors = self.df[risk_cols].replace([np.inf, -np.inf], np.nan).fillna(0)
        scaler = MinMaxScaler()
        if p == 0:
            normalized = scaler.fit_transform(risk_factors)
            self.df['risk_score'] = normalized.mean(axis=1)
            self.df['risk_level_code'] = pd.cut(self.df['risk_score'], [-0.01, 0.33, 0.66, 1.0], labels=[0, 1, 2]).astype(int)

    # Derives pseudo-news sentiment from price/volume momentum
    def add_news_column(self, window_days=10, base_threshold=0.015):
        self.df['log_return'] = np.log(self.df['Close'].shift(-window_days)) - np.log(self.df['Close'])
        mean_vol = self.df['Volume'].rolling(window=20, min_periods=1).mean()
        self.df['vol_weight'] = self.df['Volume'] / mean_vol
        self.df['weighted_return'] = self.df['log_return'] * self.df['vol_weight']

        # Define quantiles to classify returns
        upper = self.df['weighted_return'].quantile(0.80)
        upper_mid = self.df['weighted_return'].quantile(0.60)
        lower_mid = self.df['weighted_return'].quantile(0.40)
        lower = self.df['weighted_return'].quantile(0.20)

        # Classifier maps numeric return to sentiment labels
        def classify(change):
            if pd.isna(change): return 'Neutral'
            elif change > upper: return 'Very Positive'
            elif change > upper_mid: return 'Positive'
            elif change < lower: return 'Very Negative'
            elif change < lower_mid: return 'Negative'
            else: return 'Neutral'

        # Map to sentiment labels and numeric scores
        self.df['news'] = self.df['weighted_return'].apply(classify)
        sentiment_map = {'Very Negative': -2, 'Negative': -1, 'Neutral': 0, 'Positive': 1, 'Very Positive': 2}
        self.df['news_score'] = self.df['news'].map(sentiment_map)
        self.df['gap_flag'] = (self.df['Close'].pct_change().abs() > 0.05).astype(int)
        self.df['momentum_5d'] = self.df['Close'].pct_change(5)

        # Drop intermediate columns
        self.df.drop(columns=['log_return', 'vol_weight', 'weighted_return', 'news'], inplace=True, errors='ignore')

    # Adds daily trend, volatility, and return indicators
    def compute_long_term_features(self):
        self.df['price_range'] = self.df['High'] - self.df['Low']
        self.df['intraday_volatility'] = (self.df['High'] - self.df['Low']) / self.df['Open'].replace(0, np.nan)
        self.df['close_to_open'] = (self.df['Close'] - self.df['Open']) / self.df['Open'].replace(0, np.nan)
        self.df['rolling_avg_close_10'] = self.df['Close'].rolling(window=10).mean()
        self.df['rolling_std_close_10'] = self.df['Close'].rolling(window=10).std()
        self.df['rolling_return_10d'] = self.df['Close'].pct_change(10)
        self.df['news_score'] = self.df['news_score'].fillna(0)

    # Generates buy/sell signal based on 20-day return
    def compute_long_term_signal(self, forward_days=20, buy_thresh=0.04, sell_thresh=-0.04):
        self.df['future_return_20d'] = (self.df['Close'].shift(-forward_days) - self.df['Close']) / self.df['Close']

        # Label logic based on forward return
        def label(row):
            if row['future_return_20d'] > buy_thresh:
                return 1  # Buy
            elif row['future_return_20d'] < sell_thresh:
                return -1  # Sell
            else:
                return 0  # Wait

        self.df['long_term_signal'] = self.df.apply(label, axis=1)
