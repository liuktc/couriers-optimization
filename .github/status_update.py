import argparse
import json
import re
import os



def statusToOrdinal(status):
    if status == "optimal": return 0
    if status == "suboptimal": return 1
    if status == "timeout": return 2
    if status == "out-of-memory": return 3
    if status == "inconsistent": return 4


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="Update README statuses")
    parser.add_argument("--checks-file", type=str, required=True)
    parser.add_argument("--readme-file", type=str, required=True)
    parser.add_argument("--results-git-path", type=str, required=True)
    args = parser.parse_args()

    to_display_methods = ["CP", "SAT", "SMT", "MILP"]
    with open(args.checks_file, "r") as f: 
        checks = json.load(f)
    num_instances = len(checks[to_display_methods[0]])
    status_md = ""

    for i in range(1, len(to_display_methods)):
        assert to_display_methods[i] in checks
        assert len(checks[to_display_methods[i]]) == num_instances

    
    # status_md = f"| Instance | {' | '.join(to_display_methods)} |\n"
    status_md = f"| Instance | {' | '.join(['']*len(to_display_methods))} |\n"
    status_md += f"|:-:| {''.join(['---|']*(len(to_display_methods)))}\n"

    # Format badges
    for i in range(num_instances):
        instance = f"{i+1}"

        status_md += f"| {instance} | "
        for method in to_display_methods:
            if len(checks[method][instance]) == 0:
                status_md += "| "
                continue

            badge = ""

            instance_tests = [ 
                {
                    "name": test_name,
                    **status
                } 
                for test_name, status in checks[method][instance].items()
            ]
            instance_tests = sorted(instance_tests, key=lambda x: (statusToOrdinal(x["status"]), x["time"]))

            best_instance_status = instance_tests[0]["status"]
            best_instance_time = instance_tests[0]["time"]
            best_instance_name = instance_tests[0]["name"].replace("_", "__").replace("-", "--")

            if best_instance_status == "optimal":
                badge = f"https://img.shields.io/badge/{method}-{best_instance_time}_s_({best_instance_name})-brightgreen"
            elif best_instance_status == "suboptimal":
                badge = f"https://img.shields.io/badge/{method}-{best_instance_time}_s_({best_instance_name})-orange"
            elif best_instance_status == "inconsistent":
                badge = f"https://img.shields.io/badge/{method}-Inconsistent-red"
            elif best_instance_status == "timeout":
                badge = f"https://img.shields.io/badge/{method}-Timeout-lightgray"
            elif best_instance_status == "out-of-memory":
                badge = f"https://img.shields.io/badge/{method}-Out_of_memory-fedcba"
            else:
                raise Exception("Unknown status")
            
            results_path = os.path.join(args.results_git_path, method, f"{instance}.json")
            status_md += f"[![{best_instance_status}]({badge})]({results_path}) | "
        status_md += "\n"


    # Update readme
    with open(args.readme_file, "r+") as f: 
        markdown = f.read()
        f.seek(0)
        f.write(
            re.sub(
                r"<!-- begin-status -->[\s\S]*<!-- end-status -->", 
                f"<!-- begin-status -->\n{status_md}\n<!-- end-status -->", 
                markdown
            )
        )
        f.truncate()
