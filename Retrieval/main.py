# main class to start webdriver for data collection
import IntializeWebDriver as i
import GetDays as g
import os

if __name__ == "__main__":

    # Flags to control actions (set to 1 to enable)
    get_data = 1       # collect quarterly web data
    clean_data = 1     # merge and clean daily + quarterly
    compute_risk = 1   # generate risk score

    # list of stocks to process
    stocks = ["Nvidia","AMC","Apple"]

    # Initialize reusable components
    days = g.DayStockData()
    
    driver = i.Intialize()

    for idx, stock in enumerate(stocks):
        stock_dir = stock
        quarterly_path = os.path.join(stock_dir, f"{stock}_combined_quarterly.csv")
        day_to_day_path = os.path.join(stock_dir, f"{stock} day to day.csv")
        risk_path = os.path.join(stock_dir, f"{stock}.csv")

        # Step 1: Collect quarterly financial data
        if get_data and not os.path.exists(quarterly_path):
            driver.collect(stock)

        if not os.path.exists(day_to_day_path):
            days.get(stock)


    # Clean up driver after last stock
    if driver:
        driver.quit()
