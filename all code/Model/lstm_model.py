import os
import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping

class LSTMModel:
    def __init__(self, csv_path, base_dir, sequence_length=30):
        self.csv_path = csv_path
        self.base_dir = base_dir
        self.sequence_length = sequence_length

        self.df = None
        self.X_cols = []
        # add volume
        self.y_cols = ['Close', 'High', 'Low', 'long_term_signal']

        self.X_scaler = MinMaxScaler()
        self.y_scaler = MinMaxScaler()

        self.X_seq = None
        self.y_seq = None
        self.X_train = self.X_test = None
        self.y_train = self.y_test = None
        self.model = None

    def load_and_prepare_data(self):
        df = pd.read_csv(self.csv_path)

        # Keep numeric columns and clean
        df = df.select_dtypes(include=[np.number])
        df.replace([np.inf, -np.inf], np.nan, inplace=True)
        df.fillna(df.median(numeric_only=True), inplace=True)


        if 'Year' in df.columns:
            df = df[df['Year'] >= 2020]

        # Define X columns (exclude targets and future info)
        # volume taken out
        exclude_cols = ['Close', 'long_term_signal', 'future_return_20d','Volume']
        self.X_cols = [col for col in df.columns if col not in exclude_cols]

        self.df = df

    def normalize_and_split(self):
        X = self.df[self.X_cols].values
        y = self.df[self.y_cols].values

        # Normalize
        self.X_scaled = self.X_scaler.fit_transform(X)
        self.y_scaled = self.y_scaler.fit_transform(y)

        # Save scalers
        os.makedirs(self.base_dir, exist_ok=True)
        joblib.dump(self.X_scaler, os.path.join(self.base_dir, "X_scaler_final.pkl"))
        joblib.dump(self.y_scaler, os.path.join(self.base_dir, "y_scaler_final.pkl"))

        # Create sequences
        X_seq, y_seq = [], []
        for i in range(len(self.X_scaled) - self.sequence_length):
            X_seq.append(self.X_scaled[i:i + self.sequence_length])
            y_seq.append(self.y_scaled[i + self.sequence_length])

        self.X_seq = np.array(X_seq)
        self.y_seq = np.array(y_seq)

        # Train/test split
        split = int(0.8 * len(self.X_seq))
        self.X_train = self.X_seq[:split]
        self.X_test = self.X_seq[split:]
        self.y_train = self.y_seq[:split]
        self.y_test = self.y_seq[split:]

    def build_model(self):
        input_shape = (self.X_train.shape[1], self.X_train.shape[2])
        self.model = Sequential([
            LSTM(64, input_shape=input_shape),
            Dropout(0.2),
            Dense(64, activation='relu'),
            Dense(len(self.y_cols))  # Multi-output
        ])
        self.model.compile(optimizer='adam', loss='mse')
        self.model.summary()

    def train_model(self, epochs=20, batch_size=32):
        early_stop = EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)
        self.model.fit(
            self.X_train, self.y_train,
            validation_data=(self.X_test, self.y_test),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=[early_stop],
            verbose=1
        )

    def save_model_and_scalers(self):
        os.makedirs(self.base_dir, exist_ok=True)
        self.model.save(os.path.join(self.base_dir, "stock_model_final.h5"))
        joblib.dump(self.X_scaler, os.path.join(self.base_dir, "X_scaler_final.pkl"))
        joblib.dump(self.y_scaler, os.path.join(self.base_dir, "y_scaler_final.pkl"))
        joblib.dump(self.X_cols, os.path.join(self.base_dir, "X_cols_final.pkl"))


    def predict(self):
        if self.model and self.X_test is not None:
            return self.model.predict(self.X_test)
        else:
            raise ValueError("Model or input data is not ready.")
