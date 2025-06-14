import os
import json
import joblib
import pandas as pd
import sys
from tensorflow.keras.models import load_model

# Dynamically add custom module folders to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))

# Add Retrieval folder (for IntializeWebDriver and GetDays)
retrieval_path = os.path.join(current_dir, "all code", "Retrieval")
sys.path.append(retrieval_path)
from init_webdriver import Intialize as i

from GetDays import DayStockData as g

# Add Combine folder (for combine.py)
combine_path = os.path.join(current_dir, "all code", "Combine")
sys.path.append(combine_path)
import combine as c

# Add clean folder (for add_merge.py)
clean_path = os.path.join(current_dir, "all code", "clean")
sys.path.append(clean_path)
import add_merge as ra

# Add Model folder
model_path_dir = os.path.join(current_dir, "all code", "Model")
sys.path.append(model_path_dir)
import lstm_model as l  # ✅ Correct


# Add Prediction folder
predict_path = os.path.join(current_dir, "all code", "Prediction")
sys.path.append(predict_path)
import predict as p

# Add News Sentiment folder
news_sentiment_path = os.path.join(current_dir, "all code", "New Sentiment")
sys.path.append(news_sentiment_path)
import NewsSen as n


def main():
    # Toggle individual pipeline stages
    fetch_data = True              # Step 1: Scrape quarterly and daily stock data
    compute_risk = True            # Step 2: Generate financial risk scores
    combine_data = True            # Step 3: Combine cleaned stock CSVs into one
    train_model = True             # Step 4: Train LSTM model
    predict_future = True          # Step 5: Predict future stock metrics
    overwrite_existing = False     # If True, overwrite any existing files

    # Define base directories and file paths
    base_dir = r"C:\\Coding Projects\\AI stock retry\\stock"
    os.makedirs(base_dir, exist_ok=True)
    stocks = ["Nvidia", "AMC", "Apple", "Tesla"]

    combined_csv_path = os.path.join(base_dir, "all_stock_combined.csv")
    model_path = os.path.join(base_dir, "stock_model_final.h5")
    x_scaler_path = os.path.join(base_dir, "X_scaler_final.pkl")
    y_scaler_path = os.path.join(base_dir, "y_scaler_final.pkl")
    map_path = os.path.join(base_dir, "stock_id_map.json")

    # Step 1: Scrape data using Selenium (quarterly and daily)
    if fetch_data:
        print("\n🟦 Collecting raw financial data...")
        driver = i()                         # Start Selenium WebDriver
        days = g()                           # Daily stock data retriever

        for stock in stocks:
            stock_dir = os.path.join(base_dir, stock)
            os.makedirs(stock_dir, exist_ok=True)

            # Define paths for quarterly and daily CSVs
            quarterly_path = os.path.join(stock_dir, f"{stock}_combined_quarterly.csv")
            day_to_day_path = os.path.join(stock_dir, f"{stock} day to day.csv")

            # Only scrape if file doesn't exist or overwrite is enabled
            if overwrite_existing or not os.path.exists(quarterly_path):
                driver.collect(stock)

            if overwrite_existing or not os.path.exists(day_to_day_path):
                days.get(stock)

        if driver:
            driver.quit()  # Cleanly close browser

    # Step 2: Merge, clean, and compute risk scores
    if compute_risk:
        print("\n🟨 Merging and calculating risk metrics...")
        for stock in stocks:
            risk_output_path = os.path.join(base_dir, stock, f"{stock} risk.csv")
            if overwrite_existing or not os.path.exists(risk_output_path):
                analyzer = ra.RiskAnalyzer()  # Use RiskAnalyzer from add_merge
                analyzer.compute_all(stock)

    # Step 3: Combine all stock CSVs into one master CSV
    if combine_data:
        print("\n🟩 Combining all processed stocks...")
        combiner = c.StockCombiner(base_dir, stocks, combined_csv_path, map_path=map_path)
        combiner.combine()

    # Step 4: Train and save LSTM model with normalized data
    if train_model:
        print("\n🟦 Training LSTM model...")
        lstm = l.LSTMModel(combined_csv_path, base_dir)
        lstm.load_and_prepare_data()
        lstm.normalize_and_split()
        lstm.build_model()
        lstm.train_model()
        lstm.save_model_and_scalers()
        
        # Step 5: Generate predictions using news sentiment + trained model
    if predict_future:
        print("\n🟪 Generating predictions for each stock...")

        # Load trained model and scalers
        model = load_model(model_path)
        X_scaler = joblib.load(x_scaler_path)
        y_scaler = joblib.load(y_scaler_path)
        X_cols = joblib.load(os.path.join(base_dir, "X_cols_final.pkl"))

        # Load stock ID mapping
        with open(map_path, "r") as f:
            stock_id_map = json.load(f)

        for stock_name, stock_id in stock_id_map.items():
            print(f"\n📈 Predicting for: {stock_name} → ID {stock_id}")

            # Run sentiment analysis on recent news articles
            ns = n.NewsSentiment(company=stock_name, max_articles=20, ignore_seen=True)
            score = ns.analyze()
            print(f"Final news_score: {score}")

            # Load most recent stock dataset
            df_path = os.path.join(base_dir, stock_name, f"{stock_name}.csv")
            df = pd.read_csv(df_path)
            df.insert(0, "stock_id", stock_id)  # Add stock ID for multi-stock support

            # Initialize predictor with all necessary inputs
            predictor = p.StockPredictor(df, model, X_scaler, y_scaler, X_cols)

            # Predict n future trading days using LSTM
            predicted_df = predictor.predict_latest(n=1, news=score)


            # Print predicted values directly
            print("🔮 Predicted values for next 5 trading days:")
            # Print only the predicted values
            #Volume={int(row['Volume'])}
            for d, row in predicted_df.iterrows():
                print(f"Day {d+1}: Close={row['Close']:.2f}, High={row['High']:.2f}, Low={row['Low']:.2f}, , Signal={int(row['long_term_signal'])}")




# Entry point
if __name__ == "__main__":
    main()
