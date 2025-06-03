# main class to start webdriver for data collection

import os
import add_merge as ra

if __name__ == "__main__":

    # Flags to control actions (set to 1 to enable)
    get_data = 1       # collect quarterly web data
    clean_data = 1     # merge and clean daily + quarterly
    compute_risk = 1   # generate risk score

    # list of stocks to process
    stocks = ["Nvidia","AMC","Apple"]

    for idx, stock in enumerate(stocks):
        stock_dir = stock

        risk_output_path = os.path.join(stock, f"{stock} risk.csv")

        # Step 1: Collect quarterly financial data
        if not os.path.exists(risk_output_path):
            analyzer = ra.RiskAnalyzer()
            analyzer.compute_all(stock_dir)

