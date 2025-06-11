# Import necessary libraries
import pandas as pd                                      # Used for manipulating stock data and DataFrames
import pandas_market_calendars as mcal                   # Used to get valid trading days from NYSE
from datetime import datetime, timedelta                 # Used for working with time intervals
import numpy as np
# Define the stock prediction class
class StockPredictor:
    def __init__(self, df, model, X_scaler, y_scaler, X_cols):
        self.df = df
        self.model = model
        self.X_scaler = X_scaler
        self.y_scaler = y_scaler
        self.X_cols = X_cols

    def _get_future_trading_days(self, n):
        nyse = mcal.get_calendar('NYSE')
        today = pd.Timestamp.today().normalize()
        end_date = today + pd.Timedelta(days=n * 3)
        return nyse.valid_days(start_date=today, end_date=end_date)[:n]

    def predict_n_days(self, future_days, score):
        predicted_rows = []
        sequence_len = 30

        if len(self.df) < sequence_len:
            raise ValueError(f"Need at least {sequence_len} rows, but got {len(self.df)}")

        for i, date in enumerate(future_days):
            input_sequence = self.df.tail(sequence_len).copy()

            # Inject sentiment if needed
            if 'news_score' in self.X_cols:
                input_sequence['news_score'] = score

            # Check for missing features
            missing = [col for col in self.X_cols if col not in input_sequence.columns]
            if missing:
                raise ValueError(f"Missing features: {missing}")

            # Select only the expected features in the correct order
            input_sequence = input_sequence[self.X_cols]

            # Scale and reshape
            X_scaled_seq = self.X_scaler.transform(input_sequence)
            X_scaled_seq = X_scaled_seq.reshape((1, sequence_len, -1))

            # Predict
            y_scaled = self.model.predict(X_scaled_seq)
            y = self.y_scaler.inverse_transform(y_scaled)

            # Format output
            target_cols = ["Close", "High", "Low", "Volume", "long_term_signal"]
            predicted_df = pd.DataFrame(y, columns=target_cols)
            predicted_df["long_term_signal"] = predicted_df["long_term_signal"].round().astype(int)

            new_row = {}
            for col in self.df.columns:
                if col == 'Year':
                    new_row[col] = date.year
                elif col == 'Month':
                    new_row[col] = date.month
                elif col == 'Day':
                    new_row[col] = date.day
                elif col in predicted_df.columns:
                    new_row[col] = predicted_df.iloc[0][col]
                elif col in input_sequence.columns:
                    new_row[col] = input_sequence.iloc[-1][col]
                else:
                    new_row[col] = None

            predicted_rows.append(new_row)
            self.df = pd.concat([self.df, pd.DataFrame([new_row])], ignore_index=True)

        return pd.DataFrame(predicted_rows)

    def predict_latest(self, n=1, news=None):
        future_days = self._get_future_trading_days(n)
        return self.predict_n_days(future_days, news)

        # Optional debug print section (disabled by default)
        """
        print("📅 Generated future input template:")
        print(future_df)

        # Predict using the actual last n rows (for comparison/debugging)
        X_latest_scaled = self.X_scaler.transform(self.X.tail(n))
        y_pred_scaled = self.model.predict(X_latest_scaled)
        y_pred = self.y_scaler.inverse_transform(y_pred_scaled)

        predicted_df = pd.DataFrame(y_pred, columns=self.target_cols)

        print(\"\\n🔮 Predicted values (last 5 rows):\")
        print(predicted_df)

        print(\"\\n🕹 Actual y (last 5 rows):\")
        print(self.y.tail(n))

        print(\"\\n📘 Input X (last 5 rows):\")
        print(self.X.tail(n))

        return predicted_df
        """
