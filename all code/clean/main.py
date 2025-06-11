"""
Entry script to execute financial data pipeline for each stock.
This handles three steps: data collection, data cleaning/merging, and risk score computation.
Each stock gets its quarterly data merged with daily performance and exported to CSVs.
"""

# Import required modules
import os
import add_merge as ra  # Custom module that includes the RiskAnalyzer class

# Only run if this script is the entry point
if __name__ == "__main__":

    # Flags to control execution steps (set to 1 to enable)
    get_data = 1       # If enabled, collects raw quarterly financial data
    clean_data = 1     # If enabled, merges daily and quarterly datasets
    compute_risk = 1   # If enabled, computes engineered features and risk metrics

    # List of stock names to process
    stocks = ["Nvidia", "AMC", "Apple"]

    # Iterate through each stock
    for idx, stock in enumerate(stocks):
        stock_dir = stock  # Folder name per stock (e.g., 'Nvidia')

        # Construct path to check if risk output already exists
        risk_output_path = os.path.join("stock", stock, f"{stock} risk.csv")

        # If risk file not found, proceed with data processing
        if not os.path.exists(risk_output_path):
            analyzer = ra.RiskAnalyzer()  # Create RiskAnalyzer instance
            analyzer.compute_all(stock_dir)  # Run full pipeline on this stock
