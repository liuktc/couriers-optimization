# Open all the json in a specified folder
# The json is a list of dictionaries
# If the dictionary has value "test" for the key "name", remove it

import os
import json
import sys

def read_json_file(file_path):
  try:
    with open(file_path, 'r') as file:
      data = json.load(file)
      return data
  except FileNotFoundError:
    print(f"Error: File '{file_path}' not found.")
    return None
  except json.JSONDecodeError:
    print(f"Error: Unable to parse JSON from file '{file_path}'.")
    return None

def main(args):
    folder = args[1]
    for results_file in sorted(os.listdir(folder)):
        if results_file.startswith('.'):
            # Skip hidden folders.
            continue
        results = read_json_file(folder + os.sep + results_file)
        new_results = {}
        for solver, result in results.items():
            if not 'test' in solver:
                new_results[solver] = result
            else:
                print(f"Skipping {solver}")

        results = new_results
        
        with open(folder + os.sep + results_file, 'w') as file:
            json.dump(results, file, indent=2)

if __name__ == "__main__":
    main(sys.argv)