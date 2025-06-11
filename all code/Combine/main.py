# 📦 Import the StockCombiner class from the combine module
import combine as c
import os

# 🚀 Entry point for the script
if __name__ == "__main__":
    # 🧾 List of stock folders to include in the combination
    stocks = ["Nvidia", "AMC", "Apple", "Tesla"]

    # 📁 Define base directory where all individual stock folders live
    base_dir = os.path.join("stock")  # Uses relative path for GitHub compatibility

    # 📄 Define path where the combined dataset will be saved
    output_path = os.path.join(base_dir, "all_stock_combined.csv")

    # 📄 Define path for saving the stock ID mapping JSON
    map_path = os.path.join(base_dir, "stock_id_map.json")

    # 🛠 Create an instance of the StockCombiner with the above paths and stock list
    combiner = c.StockCombiner(base_dir, stocks, output_path, map_path=map_path)

    # 🧩 Combine all individual stock CSVs into one master file
    combiner.combine()
