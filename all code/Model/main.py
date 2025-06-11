"""
🔮 LSTM Model Pipeline: Stock Forecasting Core Targets 🔮

This script trains an LSTM model to predict the following daily targets:
    - Close  → Predicted closing price
    - High   → Predicted high of the day
    - Low    → Predicted low of the day
    - Volume → Predicted trading volume
    - long_term_signal → A custom model-based investment guidance signal 0 = wait -1 = sell 1 = buy

Derived metrics can be computed later using model outputs:
    🔁 Open               → Derived from previous Close (shifted)
    🔁 risk_score         → Optional; based on volatility or fundamentals
    🔁 news_score         → External value from sentiment model (FinBERT + VADER)

Example sentiment mapping:
    sentiment_map = {
        'Very Negative': -2,
        'Negative': -1,
        'Neutral': 0,
        'Positive': 1,
        'Very Positive': 2
    }
    df['news_score'] = df['news'].map(sentiment_map)


"""

# Import the LSTM model wrapper from the Model module
import model as l

import os

# Define the main function for training the LSTM model
def main():
    # Define the input CSV path containing all combined stock data
    csv_path = os.path.join("stock", "all_stock_combined.csv")  # Should be portable for GitHub

    # Define where to save the trained model and scalers
    save_path = os.path.join("stock")  # Relative to repo/project directory

    # Instantiate the LSTM class with data path and save path
    lstm = l.LSTM(csv_path, save_path)

    # Load and preprocess data (splits features and targets)
    lstm.load_and_prepare_data()

    # Normalize input features and target outputs
    lstm.normalize_and_split()

    # Build the actual Keras LSTM model structure
    lstm.build_model()

    # Train the model on historical stock data
    lstm.train_model()

    # Save the trained model and scalers for future use
    lstm.save_model_and_scalers()

# Entry point for running this script directly
if __name__ == "__main__":
    main()
