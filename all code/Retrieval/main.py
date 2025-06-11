# Libraries
import init_webdriver as i
import GetDays as g
import os

# Main script to orchestrate full data collection pipeline
if __name__ == "__main__":

    # Flags to control which steps to perform
    get_data = 1       # collect quarterly web data
    clean_data = 1     # merge and clean daily + quarterly (currently unused)
    compute_risk = 1   # generate risk score (currently unused)

    # List of company names to process
    stocks = ["Nvidia","AMC","Apple"]

    # Initialize object for getting day-to-day stock data
    days = g.DayStockData()

    # Initialize Chrome driver for scraping quarterly data
    driver = i.Intialize()

    # Ensure main "stock" directory exists
    stock_path = os.path.join("stock")
    os.makedirs(stock_path, exist_ok=True)

    # Loop through each stock
    for idx, stock in enumerate(stocks):
        stock_dir = stock

        # Define expected file paths for this stock
        quarterly_path = os.path.join("stock",stock_dir, f"{stock}_combined_quarterly.csv")
        day_to_day_path = os.path.join("stock",stock_dir, f"{stock} day to day.csv")
        risk_path = os.path.join("stock",stock_dir, f"{stock}.csv")  # (optional future step)
        stock_path = os.path.join("stock")  # redefined locally (redundant)

        # Step 1: Collect quarterly financial data if not already present
        if get_data and not os.path.exists(quarterly_path):
            driver.collect(stock)

        # Step 2: Download and save daily price data if not already downloaded
        if not os.path.exists(day_to_day_path):
            days.get(stock)

    # Step 3: Quit browser session after all stocks are processed
    if driver:
        driver.quit()
