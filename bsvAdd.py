#!/bin/python

import argparse, os, sys

def dir_path(string):
    if os.path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)

machine_temp = """BSV_TOOLS?={0}
"""

def create_machine_file(path):
    print("Creating local BSV_TOOLS path file .bsv_tools (Add to your .gitignore)")
    with open("{}/.bsv_tools".format(path), "w") as f:
        f.write(machine_temp.format(os.path.abspath(os.path.dirname(__file__))))

def main():
    parser = argparse.ArgumentParser(description="Adds machine specific info in .bsv_tools")
    parser.add_argument('--path', type=dir_path, default='./')

    args = None
    try:
        args = parser.parse_args()
    except NotADirectoryError as e:
        print("Path has to be a valid directory, got: {}.".format(e))
        sys.exit(1)

    create_machine_file(args.path)

if __name__ == "__main__":
    main()
