#!/usr/bin/env python3

import sys
import glob
import os
import re

def main():
    directory = sys.argv[1]
    builddir = sys.argv[2]
    extra_module = ""
    if(len(sys.argv) > 3):
        extra_module = sys.argv[3]
    projectModules = {}
    for filename in glob.glob(os.path.join(directory, '*.bsv')):
        m = re.match(".*/(.*).bsv", filename)
        modName = m.group(1).strip()
        projectModules[modName] = []
        with open(filename, "r") as f:
            for line in f:
                if line.strip().startswith("import"):
                    m = re.match("import(.*)::", line.strip())
                    if m:
                        mod = m.group(1).strip()
                        if mod == "`RUN_TEST":
                            mod = extra_module
                        projectModules[modName].append(mod)

    # Remove duplicates
    for module, deps in projectModules.items():
        projectModules[module] = list(set(deps))

    # Remove non project Dependencies
    for module, deps in projectModules.items():
        old = list(deps)
        for dep in old:
            if not dep in projectModules:
                deps.remove(dep)

    # Create List of modules for dependency resolution
    for m, d in projectModules.items():
        print("{}/{}.bo: {}/{}.bsv {}".format(builddir, m, directory, m, " ".join(map(lambda x : "{}/{}.bo".format(builddir, x), d))))

    depList = []
    # Produce dependency list
    while len(projectModules.keys()) > 0:
        # Look for Module without dependency
        found = False
        for m, d in projectModules.items():
            if not d:
                found = True
                depList.append(m)
                del projectModules[m]
                for _, d in projectModules.items():
                    if m in d:
                        d.remove(m)
                break
        if not found:
            print("Loop detected")
            break
    depListFull = []
    for d in depList:
        d = builddir + "/" + d + ".bo"
        depListFull.append(d)
    t = "OBJS=" + " ".join(depListFull)
    print(t)

if __name__ == '__main__':
    main()
