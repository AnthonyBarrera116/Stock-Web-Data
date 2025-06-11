# 📦 Import required libraries for data handling and file I/O
import pandas as pd
import os
import json

# 🧩 StockCombiner class: merges individual stock CSVs into one dataset and assigns unique stock IDs
class StockCombiner:
    def __init__(self, base_dir, stock_list, output_path, map_path="stock_id_map.json"):
        """
        Initialize the StockCombiner.

        Parameters:
        - base_dir: directory containing per-stock folders
        - stock_list: list of stock names to process
        - output_path: path where combined CSV will be saved
        - map_path: path to JSON file storing stock_id mappings
        """
        self.base_dir = base_dir                        # Root directory where stock folders are located
        self.stocks = stock_list                        # List of stock names (e.g., ["Apple", "Nvidia"])
        self.output_path = output_path                  # Output path for the merged CSV
        self.map_path = map_path                        # JSON path for tracking stock_id assignments
        self.stock_id_map = {}                          # Internal dictionary to hold {stock_name: stock_id}
        self.max_id = -1                                # Tracks highest stock_id used so far

    def load_id_map(self):
        """
        Load the stock_id mapping from the JSON file, if it exists.
        If it doesn't exist, initialize an empty mapping.
        """
        if os.path.exists(self.map_path):
            with open(self.map_path, 'r') as f:
                self.stock_id_map = json.load(f)                         # Load existing stock_id map
                self.max_id = max(self.stock_id_map.values(), default=-1)  # Track current max ID
        else:
            self.stock_id_map = {}
            self.max_id = -1

    def save_id_map(self):
        """
        Save the current stock_id map to the JSON file for reuse.
        """
        with open(self.map_path, 'w') as f:
            json.dump(self.stock_id_map, f, indent=2)

    def assign_stock_id(self, stock_name):
        """
        Assign a unique numeric ID to a stock if not already present in the map.

        Parameters:
        - stock_name: name of the stock (string)

        Returns:
        - Assigned numeric stock_id
        """
        if stock_name not in self.stock_id_map:
            self.max_id += 1                                      # Increment the max ID
            self.stock_id_map[stock_name] = self.max_id           # Assign to current stock
            print(f"🆕 Assigned ID {self.max_id} to new stock: {stock_name}")
        return self.stock_id_map[stock_name]

    def combine(self):
        """
        Main method to combine all stock CSV files into one unified DataFrame.
        It adds a 'stock_id' column to identify rows and saves the final combined CSV.
        """
        self.load_id_map()                     # Load existing stock ID assignments
        combined_df = []                       # List to hold all loaded DataFrames

        for stock in self.stocks:
            file_path = os.path.join(self.base_dir, stock, f"{stock}.csv")  # Path to the stock's data file

            if not os.path.exists(file_path):
                print(f"⚠️ Skipping {stock} — file not found at: {file_path}")
                continue

            df = pd.read_csv(file_path)                        # Load stock CSV
            stock_id = self.assign_stock_id(stock)             # Get or assign a unique ID
            df['stock_id'] = stock_id                          # Add stock_id column

            # Reorder columns: move stock_id to the front
            front_cols = ['stock_id']
            other_cols = [col for col in df.columns if col != 'stock_id' and col != 'stock_name']
            df = df[front_cols + other_cols]

            combined_df.append(df)                             # Add to overall dataset

        # Concatenate and save if there's at least one valid dataset
        if combined_df:
            final_df = pd.concat(combined_df, ignore_index=True)  # Merge all into one DataFrame
            final_df.to_csv(self.output_path, index=False)        # Save merged dataset
            self.save_id_map()                                    # Save updated stock_id mappings
            print(f"✅ Combined dataset saved to:\n{self.output_path}")
        else:
            print("❌ No valid stock data found to combine.")
