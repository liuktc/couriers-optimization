import argparse
import json
import re


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="Update README statuses")
    parser.add_argument("--checks-file", type=str, required=True)
    parser.add_argument("--readme-file", type=str, required=True)
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
            badge = ""

            if checks[method][instance]["status"] == "optimal":
                badge = f"https://img.shields.io/badge/{method}-{checks[method][instance]['time']}_s-brightgreen"
            elif checks[method][instance]["status"] == "suboptimal":
                badge = f"https://img.shields.io/badge/{method}-{checks[method][instance]['time']}_s-orange"
            elif checks[method][instance]["status"] == "inconsistent":
                badge = f"https://img.shields.io/badge/{method}-Inconsistent-red"
            elif checks[method][instance]["status"] == "timeout":
                badge = f"https://img.shields.io/badge/{method}-Timeout-lightgray"
            else:
                raise Exception("Unknown status")
            
            status_md += f"[![{checks[method][instance]['status']}]({badge})]({badge}) | "
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
