# main.py - This script loads a trained model and scalers, runs sentiment analysis,
# loads stock data, predicts next 5 days, and optionally saves the output.

# Import core libraries
import pandas as pd                    # For loading and manipulating stock CSV data
import joblib                          # For loading pre-saved scalers (.pkl files)
import predict as p                    # Custom prediction class with StockPredictor
from tensorflow.keras.models import load_model  # Load Keras-trained LSTM model
import json                            # For reading stock_id_map.json
import sys                             # To modify system path to access other folders
import os                              # For safe path construction across OSes

# Set current_dir to the folder where this script (amain.py) is located
current_dir = os.path.dirname(os.path.abspath(__file__))

# Set parent_dir as the folder one level above current_dir (project root)
parent_dir = os.path.dirname(current_dir)

# Construct absolute path to the folder containing NewsSentiment (custom news module)
news_sentiment_path = os.path.join(parent_dir, "all code", "New Sentiment")

# Add the NewsSentiment folder path to Python's sys.path so it can be imported
sys.path.append(news_sentiment_path)

# Import the NewsSentiment class from NewsSen.py inside the New Sentiment folder
import NewsSen as n

# Define the main execution function2019
def main():
    # Define the base directory where all stock-related files are stored
    # This resolves to something like "<repo>/stock" using current_dir
    base_dir = os.path.join(current_dir, "stock")

    # Build full path to the stock ID map JSON file
    map_path = os.path.join(base_dir, "stock_id_map.json")

    # Load the stock_id_map.json file which contains mapping of stock names to numeric IDs
    with open(map_path, "r") as f:
        stock_id_map = json.load(f)

    # Define paths to the trained model and pre-fitted scalers
    model_path = os.path.join(base_dir, "stock_model_final.h5")
    x_scaler_path = os.path.join(base_dir, "X_scaler_final.pkl")
    y_scaler_path = os.path.join(base_dir, "y_scaler_final.pkl")

    # Load the trained LSTM model from disk
    model = load_model(model_path)

    # Load the X (input features) scaler
    X_scaler = joblib.load(x_scaler_path)

    # Load the y (target output) scaler
    y_scaler = joblib.load(y_scaler_path)

    # Loop over each stock in the stock_id_map
    for stock_name, stock_id in stock_id_map.items():
        # Print which stock is currently being processed
        print(f"\n📈 Predicting for: {stock_name} → ID {stock_id}")

        # Create an instance of NewsSentiment for the current stock
        # This will pull ~20 recent news articles and analyze sentiment
        ns = n.NewsSentiment(company=stock_name, max_articles=20, ignore_seen=True)

        # Run sentiment analysis and get a final sentiment score (e.g., -2 to 2)
        score = ns.analyze()

        # Print the resulting average sentiment score for logging
        print(f"\nFinal news_score to use in model: {score}")

        # Path to the cleaned risk CSV for this stock (e.g., "Apple/Apple.csv")
        data_path = os.path.join(base_dir, stock_name, f"{stock_name}.csv")

        # Load the stock's data into a DataFrame
        df = pd.read_csv(data_path)

        # Insert the stock_id as the first column in the DataFrame
        df.insert(0, "stock_id", stock_id)

        # Initialize the StockPredictor class with the loaded data, model, and scalers
        predictor = p.StockPredictor(df, model, X_scaler, y_scaler)

        # Predict the next 5 days using the model and the latest news score
        predicted_df = predictor.predict_latest(n=5, news=score)

        # OPTIONAL: Save the predictions to a CSV file
        # output_path = os.path.join(base_dir, stock_name, f"{stock_name}_predicted_next_5_days.csv")
        # predicted_df.to_csv(output_path, index=False)
        # print(f"✅ Saved predictions to: {output_path}")

# Standard Python entry point for standalone script execution
if __name__ == "__main__":
    main()
