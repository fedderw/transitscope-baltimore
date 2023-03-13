### Write a function that calls the node script located in transitscope-baltimore/mta-bus-ridership-scraper
import subprocess
import os
import sys
from pathlib import Path
import pandas as pd

def run_node_script():
    # Get the current working directory
    cwd = os.getcwd()
    print(cwd)
    # Get the path to the node script
    node_script_path = os.path.join(cwd, "mta-bus-ridership-scraper", "index.js")
    # Run the node script
    subprocess.run(["node", node_script_path])
    # move mta-bus-ridership.csv to data/raw
    raw_data_path = os.path.join(cwd, "data", "raw")
    subprocess.run(["mv", "mta-bus-ridership.csv", raw_data_path])
    # Compress the raw data
    subprocess.run(["gzip", os.path.join(raw_data_path, "mta-bus-ridership.csv")])
    
if __name__ == "__main__":
    run_node_script()
