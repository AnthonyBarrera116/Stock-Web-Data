"""
Collect Financial Data Scraper

This script uses Selenium and custom tools to extract financial data for a given stock from macrotrends.net.
It collects and merges multiple data sources into a single cleaned CSV file.

Columns in the output CSV:
- Date: Financial report date

Financials:
- financials_Revenue: Total company revenue
- financials_Cost Of Goods Sold: Direct costs to produce goods
- financials_Gross Profit: Revenue - COGS
- financials_Research And Development Expenses: R&D spending
- financials_SG&A Expenses: Selling, General & Administrative expenses
- financials_Other Operating Income Or Expenses: Misc. operating items
- financials_Operating Expenses: Total operating costs
- financials_Operating Income: Income from core operations
- financials_Total Non-Operating Income/Expense: Gains/losses not from core ops
- financials_Pre-Tax Income: Income before taxes
- financials_Income Taxes: Tax expense
- financials_Income After Taxes: Net of taxes
- financials_Other Income: Additional income not categorized
- financials_Income From Continuous Operations: Ongoing business income
- financials_Income From Discontinued Operations: One-off closed ops income
- financials_Net Income: Final profit after all expenses
- financials_EBITDA: Earnings before interest, taxes, depreciation, amortization
- financials_EBIT: Earnings before interest and taxes
- financials_Basic Shares Outstanding: Number of basic shares
- financials_Shares Outstanding: Total shares issued
- financials_Basic EPS: Basic Earnings Per Share
- financials_EPS - Earnings Per Share: Overall EPS

Balance Sheet:
- balance_sheet_Cash On Hand: Liquid cash
- balance_sheet_Receivables: Outstanding customer payments
- balance_sheet_Inventory: Goods on hand for sale
- balance_sheet_Pre-Paid Expenses: Advance payments for future services
- balance_sheet_Other Current Assets: Misc. short-term assets
- balance_sheet_Total Current Assets: Sum of all current assets
- balance_sheet_Property Plant And Equipment: Tangible fixed assets
- balance_sheet_Long-Term Investments: Investments held long-term
- balance_sheet_Goodwill And Intangible Assets: Intangible value (IP, goodwill)
- balance_sheet_Other Long-Term Assets: Misc. long-term assets
- balance_sheet_Total Long-Term Assets: Sum of all long-term assets
- balance_sheet_Total Assets: Total assets owned
- balance_sheet_Total Current Liabilities: Near-term obligations
- balance_sheet_Long Term Debt: Debt due after 1 year
- balance_sheet_Other Non-Current Liabilities: Long-term non-debt liabilities
- balance_sheet_Total Long Term Liabilities: All long-term obligations
- balance_sheet_Total Liabilities: Total liabilities
- balance_sheet_Common Stock Net: Equity from common stock
- balance_sheet_Retained Earnings (Accumulated Deficit): Accumulated profit/loss
- balance_sheet_Comprehensive Income: All-inclusive earnings
- balance_sheet_Other Share Holders Equity: Misc. equity entries
- balance_sheet_Share Holder Equity: Total equity from shareholders
- balance_sheet_Total Liabilities And Share Holders Equity: Total capitalization

Cash Flow:
- cash_flow_statement_Net Income/Loss: Bottom line net income
- cash_flow_statement_Total Depreciation And Amortization - Cash Flow: Non-cash expense
- cash_flow_statement_Other Non-Cash Items: Misc. adjustments
- cash_flow_statement_Total Non-Cash Items: Total of all non-cash changes
- cash_flow_statement_Change In Accounts Receivable: Cash impact from receivables
- cash_flow_statement_Change In Inventories: Inventory working capital change
- cash_flow_statement_Change In Accounts Payable: Payables impact
- cash_flow_statement_Change In Assets/Liabilities: Misc. changes
- cash_flow_statement_Total Change In Assets/Liabilities: Net working capital flow
- cash_flow_statement_Cash Flow From Operating Activities: Core cash generation
- cash_flow_statement_Net Change In Property Plant And Equipment: CapEx
- cash_flow_statement_Net Change In Intangible Assets: Spending on intangibles
- cash_flow_statement_Net Acquisitions/Divestitures: M&A activity
- cash_flow_statement_Net Change In Short-term Investments: Short-term investing flow
- cash_flow_statement_Net Change In Long-Term Investments: Long-term investment flow
- cash_flow_statement_Net Change In Investments - Total: Total investing flow
- cash_flow_statement_Investing Activities - Other: Other investing changes
- cash_flow_statement_Cash Flow From Investing Activities: Total investing cash flow
- cash_flow_statement_Net Long-Term Debt: New vs. repaid long-term debt
- cash_flow_statement_Net Current Debt: Short-term debt activity
- cash_flow_statement_Debt Issuance/Retirement Net - Total: Total debt movement
- cash_flow_statement_Net Common Equity Issued/Repurchased: Stock issuance/buybacks
- cash_flow_statement_Net Total Equity Issued/Repurchased: Equity activity
- cash_flow_statement_Total Common And Preferred Stock Dividends Paid: Dividends
- cash_flow_statement_Financial Activities - Other: Other financing flows
- cash_flow_statement_Cash Flow From Financial Activities: Total financing cash
- cash_flow_statement_Net Cash Flow: Total net change in cash
- cash_flow_statement_Stock-Based Compensation: Equity comp for employees
- cash_flow_statement_Common Stock Dividends Paid: Dividend cash flow

Key Ratios:
- key_financial_ratios_Current Ratio: Current assets / liabilities
- key_financial_ratios_Long-term Debt / Capital: Leverage measure
- key_financial_ratios_Debt/Equity Ratio: Total debt / shareholder equity
- key_financial_ratios_Gross Margin: Gross profit / revenue
- key_financial_ratios_Operating Margin: Operating income / revenue
- key_financial_ratios_EBIT Margin: EBIT / revenue
- key_financial_ratios_EBITDA Margin: EBITDA / revenue
- key_financial_ratios_Pre-Tax Profit Margin: Pre-tax income / revenue
- key_financial_ratios_Net Profit Margin: Net income / revenue
- key_financial_ratios_Asset Turnover: Revenue / assets
- key_financial_ratios_Inventory Turnover Ratio: COGS / inventory
- key_financial_ratios_Receiveable Turnover: Revenue / receivables
- key_financial_ratios_Days Sales In Receivables: Avg collection time
- key_financial_ratios_ROE - Return On Equity: Net income / shareholder equity
- key_financial_ratios_Return On Tangible Equity: Net income / tangible equity
- key_financial_ratios_ROA - Return On Assets: Net income / assets
- key_financial_ratios_ROI - Return On Investment: Return / invested capital
- key_financial_ratios_Book Value Per Share: Equity per share
- key_financial_ratios_Operating Cash Flow Per Share: Operating cash / share
- key_financial_ratios_Free Cash Flow Per Share: Free cash flow / share

- Employees: Number of company employees
"""

# Libraries
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import os

# Program files made as tools
import ScrollAndTools as t

# collection class
class Collect:

    # intilizes tools and ad removal with driver made from IntializeWebDriver.py
    def __init__(self, driver):

        # web driver from Intialize class
        self.driver = driver

        # scrolling tools and clicking tools from ScrollAndTools.py
        self.tools = t.Tools(self.driver)

        # stock name placeholder
        self.name = None

        # chart tabs to extract from web (each has a table)
        self.charts = [
            "Financials",
            "Balance Sheet",
            "Cash Flow Statement",
            "Key Financial Ratios",
            "Other Metrics"
        ]

    # collects all financial data from all chart tabs
    def collect_stock_info(self, stock_name):

        # set stock name
        self.name = stock_name

        # search for stock on macrotrends
        self.tools.search(self.name)

        # empty df to store all data
        combined_df = None

        # loop through each tab
        for chart_title in self.charts:

            # special case: employee count inside "Other Metrics"
            if chart_title.lower() == "other metrics":

                # click tab and nested section
                self.tools.click(chart_title)
                self.tools.click("Employee Count", nested=True)

                # extract employee count table
                df = self.extract_employee_table_to_df()

                # if table isn't empty
                if not df.empty:

                    # convert to numbers
                    df['Year'] = pd.to_numeric(df['Year'], errors='coerce').fillna(0).astype(int)
                    df['Employees'] = pd.to_numeric(df['Employees'], errors='coerce').fillna(0).astype(int)

                    # merge into combined df using Year
                    if combined_df is not None and 'Date' in combined_df.columns:

                        combined_df = combined_df.copy()
                        combined_df['Date'] = pd.to_datetime(combined_df['Date'], errors='coerce')
                        combined_df['Year'] = combined_df['Date'].dt.year.fillna(0).astype(int)

                        combined_df = combined_df.iloc[1:].copy()

                        print(combined_df)
                        print(df[['Year', 'Employees']])

                        # safe merge
                        merged_df = combined_df.merge(df[['Year', 'Employees']], how='left', on='Year')
                        merged_df.drop(columns=['Year'], inplace=True)
                        combined_df = merged_df
                    else:
                        print("Warning: No valid 'Date' column in combined_df to derive 'Year'. Skipping merge.")
                else:
                    print("Warning: Empty employee count table.")

            # all other financial chart tabs
            else:
                self.tools.click(chart_title)
                self.tools.quartely()

                # extract chart table and clean it
                df = self.get_chart()

                # convert missing to 0
                df.replace("-", 0, inplace=True)

                # remove $ % , symbols so we can make numbers
                df = df.applymap(lambda x: str(x).replace("$", "").replace(",", "").replace("%", "") if isinstance(x, str) else x)
                df = df.apply(pd.to_numeric, errors='ignore')

                # transpose: dates = rows
                df_t = df.set_index(df.columns[0]).T.reset_index()
                df_t.rename(columns={"index": "Date"}, inplace=True)

                # prefix columns based on which tab they came from
                prefix = chart_title.lower().replace(" ", "_").replace("__", "_")
                df_t = df_t.rename(columns=lambda x: f"{prefix}_{x}" if x != "Date" else x)

                # merge to final table
                if combined_df is None:
                    combined_df = df_t
                else:
                    combined_df = pd.merge(combined_df, df_t, on="Date", how="outer")

        # If we got data, format it nicely
        if combined_df is not None:

            # fix Date formatting
            combined_df['Date'] = pd.to_datetime(combined_df['Date'], errors='coerce')
            combined_df.sort_values(by="Date", inplace=True)
            # make folder and save path
            combined_csv_path = os.path.join(os.getcwd(),"stock",self.name, f"{self.name}_combined_quarterly.csv")
            #os.makedirs(self.name, exist_ok=True)

            # make sure everything but Date is clean
            combined_df.replace("-", 0, inplace=True)

            for col in combined_df.columns:
                if col != "Date":
                    combined_df[col] = combined_df[col].astype(str)
                    combined_df[col] = combined_df[col].str.replace(r"[\$,%,]", "", regex=True)
                    combined_df[col] = pd.to_numeric(combined_df[col], errors="coerce").fillna(0)

            # save final merged table
            combined_df.to_csv(combined_csv_path, index=False)
            print(f"\nSaved merged data to: {combined_csv_path}")

        # if nothing scraped
        else:
            print("\nNo data collected.")

    # special method just to get employee count table from the "Other Metrics" tab
    def extract_employee_table_to_df(self):

        # list to store each row of data
        data = []

        try:
            # find all rows in the employee count table
            rows = self.driver.find_elements(By.CSS_SELECTOR, "table.historical_data_table tbody tr")

            # loop through each row
            for row in rows:

                # get columns (should be year and employee count)
                cols = row.find_elements(By.TAG_NAME, "td")

                # if exactly 2 columns (expected format)
                if len(cols) == 2:

                    # extract year (left column) and clean it
                    year = cols[0].text.strip()

                    # extract employee count (right column), remove commas for parsing
                    employees = cols[1].text.strip().replace(',', '')

                    # add to list (set employees to 0 if it's "N/A")
                    data.append({
                        "Year": int(year),
                        "Employees": 0 if employees == 'N/A' else int(employees)
                    })

            # return as pandas DataFrame
            return pd.DataFrame(data)

        # handle error if element not found or page not loaded
        except Exception as e:
            print(f"Error while extracting data: {e}")
            return pd.DataFrame()  # return empty DataFrame if error occurs

    # gets chart data from financial tables (jqxgrid) by scrolling horizontally
    def get_chart(self):

        # scroll down slightly to make grid visible
        self.tools.scroll_down(150)

        # wait until jqxgrid element appears (holds the table)
        WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.ID, "jqxgrid")))
        time.sleep(5)  # extra buffer to let grid fully render

        # extract all currently visible header labels and table rows
        all_headers, all_data = self.tools.extract_grid_data()

        # max number of scrolls to try (avoids infinite loop)
        max_scroll_attempts = 50
        attempts = 0

        # keep scrolling until no new date columns appear
        while attempts < max_scroll_attempts:

            # get scrollbar position before scroll
            x_before = self.tools.get_scrollbar_thumb_x()
            if x_before is None:
                break  # if scroll bar not detected, exit

            # drag scrollbar to right
            scrolled = self.tools.drag_scrollbar(100)
            time.sleep(2)  # allow time for new content to load

            # get scrollbar position after scroll
            x_after = self.tools.get_scrollbar_thumb_x()

            # if no movement happened or scrollbar disappeared, stop
            if x_after is None or x_after <= x_before:
                break

            # extract new headers and data after scroll
            new_headers, new_data = self.tools.extract_grid_data()

            # find new date columns (headers that look like dates and weren’t already seen)
            new_date_cols = [h for h in new_headers if self.tools.looks_like_date(h) and h not in all_headers]

            # if no new date columns found, stop
            if not new_date_cols:
                break

            # get the indices of new columns
            new_indices = [new_headers.index(h) for h in new_date_cols]

            # loop through each row and extract new column values
            for i, row in enumerate(new_data):

                # get values at new date indices, or empty string if not available
                row_data = [row[idx] if idx < len(row) else '' for idx in new_indices]

                # extend existing rows or create new ones
                if i < len(all_data):
                    all_data[i].extend(row_data)
                else:
                    all_data.append([''] * len(all_headers) + row_data)

            # add new headers to master list
            all_headers.extend(new_date_cols)
            attempts += 1  # increment scroll attempts

        # ensure each row has same number of columns (pad or truncate)
        for i in range(len(all_data)):
            if len(all_data[i]) < len(all_headers):
                all_data[i] += [''] * (len(all_headers) - len(all_data[i]))  # pad with blanks
            elif len(all_data[i]) > len(all_headers):
                all_data[i] = all_data[i][:len(all_headers)]  # truncate extra data

        # convert final data to pandas DataFrame with headers
        return pd.DataFrame(all_data, columns=all_headers)