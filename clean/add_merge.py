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

# Libraries
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import os

class RiskAnalyzer:

    def __init__(self, df=None):
        self.df = None        # Quarterly financials
        self.days = None      # Daily stock data

    def compute_all(self, s):
        # Load & merge
        day_path = os.path.join(s, f"{s} day to day.csv")
        fin_path = os.path.join(s, f"{s}_combined_quarterly.csv")
        self.days = pd.read_csv(day_path)
        self.df = pd.read_csv(fin_path)
        self.days['Date'] = pd.to_datetime(self.days['Date'], errors='coerce')
        self.df['Date'] = pd.to_datetime(self.df['Date'], errors='coerce')
        merged_df = self.merge_quarterly_day_to_day()

        # Store merged base and track original columns
        self.df = merged_df.copy()
        original_cols = set(self.df.columns)

        # Feature engineering
        self.df['Year'] = self.df['Date'].dt.year
        self.df['Day'] = self.df['Date'].dt.dayofyear
        self.compute_volatility()
        self.compute_financial_risk()
        self.compute_earnings_risk()
        self.compute_operational_risk()
        self.compute_composite_risk()
        self.add_news_column(base_threshold=0.015)
        self.compute_long_term_features()
        self.compute_long_term_signal()

        # Save full risk-enhanced merged dataset
        full_output_path = os.path.join(s, f"{s}.csv")
        self.df.to_csv(full_output_path, index=False)

        # Identify only new engineered features
        new_cols = [col for col in self.df.columns if col not in original_cols and col != 'Date']
        risk_only_df = self.df[['Date'] + new_cols].copy()

        # Fill NaNs with 0 in new engineered features
        risk_only_df[new_cols] = risk_only_df[new_cols].fillna(0)
        self.df[new_cols] = self.df[new_cols].fillna(0)

        # Save risk-only features
        risk_only_path = os.path.join(s, f"{s} risk only.csv")
        risk_only_df.to_csv(risk_only_path, index=False)

    def merge_quarterly_day_to_day(self):
        if isinstance(self.days.columns, pd.MultiIndex):
            self.days.columns = [col[0] for col in self.days.columns.values]

        self.df = self.df.drop_duplicates(subset='Date')
        self.df = self.df.sort_values('Date')
        self.days = self.days.drop_duplicates(subset='Date')
        self.days = self.days.sort_values('Date')

        self.df.set_index('Date', inplace=False)
        self.days.set_index('Date', inplace=False)

        emp_df = None
        if 'Employees' in self.df.columns:
            emp_df = self.df[['Date', 'Employees']].drop_duplicates().sort_values('Date')
            self.df = self.df.drop(columns=['Employees'])

        merged = pd.merge_asof(
            self.days.sort_values('Date'),
            self.df.sort_values('Date'),
            on='Date',
            direction='backward'
        )

        if emp_df is not None:
            merged = pd.merge_asof(
                merged.sort_values('Date'),
                emp_df.sort_values('Date'),
                on='Date',
                direction='backward'
            )

        self.df = merged.copy()
        return merged

    def compute_volatility(self):
        self.df['daily_return'] = self.df['Close'].pct_change()
        self.df['volatility_10d'] = self.df['daily_return'].rolling(window=10).std()
        self.df['volatility_30d'] = self.df['daily_return'].rolling(window=30).std()
        self.df['rolling_max'] = self.df['Close'].cummax()
        self.df['drawdown'] = self.df['Close'] / self.df['rolling_max'] - 1
        self.df['max_drawdown'] = self.df['drawdown'].rolling(window=30).min()

    def compute_financial_risk(self):
        self.df['quick_ratio'] = (
            self.df['balance_sheet_Cash On Hand'] + self.df['balance_sheet_Receivables']
        ) / self.df['balance_sheet_Total Current Liabilities']
        self.df['debt_ratio'] = (
            self.df['balance_sheet_Total Liabilities'] / self.df['balance_sheet_Total Assets']
        )
        self.df['cash_burn'] = -self.df['cash_flow_statement_Cash Flow From Operating Activities']
        self.df['months_of_cash'] = self.df['balance_sheet_Cash On Hand'] / (self.df['cash_burn'] / 12)

    def compute_earnings_risk(self):
        self.df['eps_change_qoq'] = self.df['financials_EPS - Earnings Per Share'].pct_change()
        self.df['margin_trend'] = (
            self.df['key_financial_ratios_Net Profit Margin'].rolling(window=3).mean()
        )

    def compute_operational_risk(self):
        self.df['rd_intensity'] = (
            self.df['financials_Research And Development Expenses'] / self.df['financials_Revenue']
        )
        self.df['earnings_quality'] = (
            self.df['cash_flow_statement_Total Non-Cash Items'] /
            self.df['cash_flow_statement_Net Income/Loss']
        )

    def compute_composite_risk(self):
        risk_cols = [
            'volatility_30d', 'debt_ratio', 'cash_burn',
            'eps_change_qoq', 'earnings_quality'
        ]
        risk_factors = self.df[risk_cols].replace([np.inf, -np.inf], np.nan).fillna(0)
        scaler = MinMaxScaler()
        normalized = scaler.fit_transform(risk_factors)
        self.df['risk_score'] = normalized.mean(axis=1)
        self.df['risk_level_code'] = pd.cut(
            self.df['risk_score'], bins=[-0.01, 0.33, 0.66, 1.0],
            labels=[0, 1, 2]
        ).astype(int)

    def add_news_column(self, window_days=10, use_volume_weighting=True,
                        use_percentile_threshold=True, base_threshold=0.015,
                        add_gap_flag=True, add_momentum=True):

        df = self.df.copy()

        df['log_return'] = np.log(df['Close'].shift(-window_days)) - np.log(df['Close'])

        if use_volume_weighting and 'Volume' in df.columns:
            mean_vol = df['Volume'].rolling(window=20, min_periods=1).mean()
            df['vol_weight'] = df['Volume'] / mean_vol
            df['weighted_return'] = df['log_return'] * df['vol_weight']
        else:
            df['weighted_return'] = df['log_return']

        if use_percentile_threshold:
            upper = df['weighted_return'].quantile(0.80)
            upper_mid = df['weighted_return'].quantile(0.60)
            lower_mid = df['weighted_return'].quantile(0.40)
            lower = df['weighted_return'].quantile(0.20)
        else:
            upper = base_threshold * 2
            upper_mid = base_threshold
            lower_mid = -base_threshold
            lower = -base_threshold * 2

        def classify(change):
            if pd.isna(change):
                return 'Neutral'
            elif change > upper:
                return 'Very Positive'
            elif change > upper_mid:
                return 'Positive'
            elif change < lower:
                return 'Very Negative'
            elif change < lower_mid:
                return 'Negative'
            else:
                return 'Neutral'

        df['news'] = df['weighted_return'].apply(classify)

        sentiment_map = {
            'Very Negative': -2,
            'Negative': -1,
            'Neutral': 0,
            'Positive': 1,
            'Very Positive': 2
        }
        df['news_score'] = df['news'].map(sentiment_map)

        if add_gap_flag:
            df['gap_flag'] = df['Close'].pct_change().abs() > 0.05
        df['gap_flag'] = df['gap_flag'].astype(int)

        if add_momentum:
            df['momentum_5d'] = df['Close'].pct_change(5)

        df.drop(columns=['log_return', 'vol_weight', 'weighted_return'], errors='ignore', inplace=True)

        self.df = df

    def compute_long_term_features(self):
        df = self.df
        df['price_range'] = df['High'] - df['Low']
        df['intraday_volatility'] = (df['High'] - df['Low']) / df['Open'].replace(0, np.nan)
        df['close_to_open'] = (df['Close'] - df['Open']) / df['Open'].replace(0, np.nan)
        df['rolling_avg_close_10'] = df['Close'].rolling(window=10).mean()
        df['rolling_std_close_10'] = df['Close'].rolling(window=10).std()
        df['rolling_return_10d'] = df['Close'].pct_change(10)
        df['news_score'] = df['news_score'].fillna(0)
        self.df.drop(columns=['news'], inplace=True, errors='ignore')
        self.df = df

    def compute_long_term_signal(self, forward_days=20, buy_thresh=0.10, sell_thresh=-0.07):
        self.df['future_return_20d'] = (
            self.df['Close'].shift(-forward_days) - self.df['Close']
        ) / self.df['Close']

        def label(row):
            if row['future_return_20d'] > buy_thresh:
                return 'Buy'
            elif row['future_return_20d'] < sell_thresh:
                return 'Sell'
            else:
                return 'Wait'

        self.df['long_term_signal'] = self.df.apply(label, axis=1)
        signal_map = {'Buy': 1, 'Wait': 0, 'Sell': -1}
        self.df['long_term_signal'] = self.df['long_term_signal'].map(signal_map)
