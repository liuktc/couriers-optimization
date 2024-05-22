import os
import re
import sys
import json

TIMEOUT = 300
# OPT[i] = Optimal value for instance i.
OPT = [None, 14, 226, 12, 220, 206]

OPTIMAL_STR = "optimal"
SUBOPTIMAL_STR = "suboptimal"
INCONSISTENT_STR = "inconsistent"
TIMEOUT_STR = "timeout"


def read_json_file(file_path):
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: Unable to parse JSON from file '{file_path}'.")
        return None


def didTimeout(result):
    return (result["time"] < 0 or result["time"] > TIMEOUT)


def isInconsistent(result, instance_num, n_items, dist_matrix, sizes, capacity):
    if "sol" not in result or not result["sol"] or result["sol"] == "N/A":
        return True
    
    max_dist = 0
    n_collected = sum(len(p) for p in result["sol"])
    if n_collected != n_items:
        return True

    courier_id = 0
    for path in result["sol"]:
        dist = 0
        path_size = 0
        # Adjusting with origin point.
        path = [n_items + 1] + path + [n_items + 1]
        for i in range(1, len(path)):
            curr_item = path[i] - 1
            prev_item = path[i - 1] - 1
            dist += dist_matrix[prev_item][curr_item]
            if i < len(path) - 1:
                path_size += sizes[curr_item]
        if path_size > capacity[courier_id]:
            return True
        if dist > max_dist:
            max_dist = dist
            max_path = path
            max_cour = courier_id
        courier_id += 1

    if max_dist != result["obj"]:
        return True
    
    if instance_num < 6 and result["optimal"] and result["obj"] != OPT[instance_num]:
        return True
            
    return False


def isSuboptimal(result):
    return not result["optimal"]


def isOptimal(result):
    return result["optimal"]



def main(args):
    """
    check_solution.py <input folder> <results folder>
    """
    # FIXME: Input folder contains the input files (in the format instXY.dat).
    #       The results folder contains the .json file of each approach.
    #       No other file should appear in these folders.
    errors = []
    warnings = []

    instances_status = {}

    results_folder = args[2]
    for subfolder in os.listdir(results_folder):
        if subfolder.startswith("."):
            # Skip hidden folders.
            continue
        folder = results_folder + subfolder

        instances_status[subfolder] = {}

        # print(f"\nChecking results in {folder} folder")
        for results_file in sorted(os.listdir(folder)):
            if results_file.startswith("."):
                # Skip hidden folders.
                continue
            results = read_json_file(folder + "/" + results_file)
            # print(f"\tChecking results for instance {results_file}")
            inst_number = re.search("\d+", results_file).group()


            inst_number_int = int(inst_number)
            instances_status[subfolder][inst_number_int] = {}
            
            
            if len(inst_number) == 1:
                inst_number = "0" + inst_number
            inst_path = args[1] + "/inst" + inst_number + ".dat"
            # print(f"\tLoading input instance {inst_path}")
            with open(inst_path) as inst_file:
                i = 0
                for line in inst_file:
                    if i == 0:
                        n_couriers = int(line)
                    elif i == 1:
                        n_items = int(line)
                        dist_matrix = [None] * (n_items + 1)
                    elif i == 2:
                        capacity = [int(x) for x in line.split()]
                        assert len(capacity) == n_couriers
                    elif i == 3:
                        sizes = [int(x) for x in line.split()]
                        assert len(sizes) == n_items
                    else:
                        row = [int(x) for x in line.split()]
                        assert len(row) == n_items + 1
                        dist_matrix[i - 4] = [int(x) for x in row]
                    i += 1
            for i in range(len(dist_matrix)):
                assert dist_matrix[i][i] == 0

            for solver, result in results.items():
                if didTimeout(result):
                    instances_status[subfolder][inst_number_int][solver] = {
                        "status": TIMEOUT_STR,
                        "time": result["time"]
                    }
                elif isInconsistent(result, inst_number_int, n_items, dist_matrix, sizes, capacity):
                    instances_status[subfolder][inst_number_int][solver] = {
                        "status": INCONSISTENT_STR,
                        "time": result["time"]
                    }
                elif isSuboptimal(result):
                    instances_status[subfolder][inst_number_int][solver] = {
                        "status": SUBOPTIMAL_STR,
                        "time": result["time"]
                    }
                elif isOptimal(result):
                    instances_status[subfolder][inst_number_int][solver] = {
                        "status": OPTIMAL_STR,
                        "time": result["time"]
                    }
                else:
                    raise Exception("Case not handled")

    print(json.dumps(instances_status, indent=4))


if __name__ == "__main__":
    main(sys.argv)
