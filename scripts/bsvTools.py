#!/usr/bin/env python3

import sys
import subprocess
import argparse
import os
import shutil
import glob
import subprocess
import re
from shutil import which

vendor = "esa.informatik.tu-darmstadt.de"
createNewProject = """
ipx::infer_core -vendor {vendor} -name {projectname} -library user -taxonomy /UserIP -files {directory}/src/{topModule}.v -root_dir {directory}
ipx::edit_ip_in_project -upgrade true -name edit_ip_project -directory {tmpdir} {directory}/component.xml
ipx::current_core {directory}/component.xml
set_property top {topModule} [current_fileset]
set_property -quiet interface_mode monitor [ipx::get_bus_interfaces *MON* -of_objects [ipx::current_core]]
add_files {directory}/src
update_compile_order -fileset sources_1
set_property name {projectname} [ipx::current_core]
set_property display_name {projectname} [ipx::current_core]
set_property description {projectname} [ipx::current_core]
set_property core_revision 1 [ipx::current_core]
set_property supported_families {{zynq Pre-Production virtex7 Pre-Production kintex7 Pre-Production artix7 Pre-Production zynquplus Pre-Production virtex7 Pre-Production qvirtex7 Pre-Production kintex7 Pre-Production kintex7l Pre-Production qkintex7 Pre-Production qkintex7l Pre-Production artix7 Pre-Production artix7l Pre-Production aartix7 Pre-Production qartix7 Pre-Production zynq Pre-Production qzynq Pre-Production azynq Pre-Production spartan7 Pre-Production virtexu Pre-Production virtexuplus Pre-Production virtexuplusHBM Pre-Production kintexuplus Pre-Production zynquplus Pre-Production kintexu Pre-Production versal Pre-Production}} [ipx::current_core]
foreach f {{ {includes} }} {{
    set_property is_global_include true [get_files $f]
}}
update_compile_order -fileset sources_1
update_compile_order -fileset sim_1
ipx::merge_project_changes files [ipx::current_core]
ipx::merge_project_changes ports [ipx::current_core]
puts "USED FILES"
foreach f [ipx::get_files -of_objects [ipx::get_file_groups *synthesis*]] {{
    set n [get_property NAME $f]
    puts "USED FILE:$n"
}}
puts "END USED FILES"
puts "Additional Parameters"
{additional_parameters}
puts "End Additional Parameters"
ipx::create_xgui_files [ipx::current_core]
ipx::update_checksums [ipx::current_core]
ipx::save_core [ipx::current_core]
close_project -delete
puts "VIVADO FINISHED SUCCESSFULLY"
"""

def copyBSVVerilog(src, dest):
    for filename in glob.glob(os.path.join(src, 'Verilog', '*.v')):
        shutil.copy(filename, dest)
    for filename in glob.glob(os.path.join(src, 'Verilog.Vivado', '*.v')):
        shutil.copy(filename, dest)

def copyNGC(src, dest, exclude):
    for path in src:
        if path.endswith('.ngc'):
            if not os.path.basename(path) in exclude:
                    shutil.copy(path, dest)

def copyVerilog(src, dest, exclude):
    for path in src:
        if path.endswith('.v') or path.endswith('.vhd') or path.endswith('.h') or path.endswith('.sv'):
            if not os.path.basename(path) in exclude:
                    flattenVerilogIncludes(path, dest)
        else:
            verilogfiles = glob.glob(os.path.join(path, '*.v'))
            sysverilogfiles = glob.glob(os.path.join(path, '*.sv'))
            vhdlfiles = glob.glob(os.path.join(path, '*.vhd'))
            headerfiles = glob.glob(os.path.join(path, '*.h'))
            allfiles = verilogfiles + vhdlfiles + headerfiles + sysverilogfiles
            for filename in allfiles:
                if not os.path.basename(filename) in exclude:
                    flattenVerilogIncludes(filename, dest)

def executeVivado(tcl, vendor, projectname, ippath, tmpdir, topModule, additional, includes):
    if which("vivado") is None:
        print("Could not find \"vivado\". Make sure Vivado is in the path.")
        sys.exit(1)
    with open('temp.tcl', "w+") as f:
        f.write(tcl.format(vendor=vendor,directory=ippath,projectname=projectname,tmpdir=tmpdir,topModule=topModule, additional_parameters=additional, includes=" ".join(includes)))
    t = subprocess.Popen("vivado -mode batch -source temp.tcl -nojournal -nolog", shell=True, stdout=subprocess.PIPE).stdout.read()
    os.remove('temp.tcl')
    usedfiles = []
    s = t.decode()
    success = re.search(r"VIVADO FINISHED SUCCESSFULLY", s)
    if success:
        print("Vivado finished successfully.")
    else:
        print(s)
        print("Vivado failed. Check above log for errors.")
        sys.exit(1)

    for l in t.splitlines():
        if l.startswith(b"USED FILE:"):
            lt = l.split(b':')
            usedfiles.append(lt[1].decode("utf-8") )
    return usedfiles

def removeUnused(used, srcpath):
    for filename in os.listdir(srcpath):
        fullname = os.path.join(srcpath, filename)
        if not fullname in used:
            os.unlink(fullname)

def flattenVerilogIncludes(src, dst):
    with open(src, "r") as src_file:
        dstFilename = dst + '/' + os.path.basename(src)
        with open(dstFilename, "w") as dst_file:
            for l in src_file:
                m = re.search("^\s*`include \"(.*)\"", l)
                if m:
                    dst_file.write("`include \"" + os.path.basename(m.group(1)) + "\"")
                else:
                    dst_file.write(l)

def parseConstraints(s):
    constraints = []
    for c in s:
        if c:
            try:
                p, t = c.split(',')
            except:
                print("Constraints have to be provided in the format PATH,LOAD_PRIORITY")
                sys.exit()
            load_times = ["LATE", "NORMAL", "EARLY"]
            if not t in load_times:
                print("Load priority has to be one of {}".format(load_times))
                sys.exit()
            constraints.append({"path":p, "priority":t})
    return constraints

def processConstraints(s, p):
    additional = ""
    if s:
        os.makedirs(p)
        for t in s:
            cp = t["path"]
            ct = t["priority"]
            filename = os.path.basename(cp)
            shutil.copyfile(cp, p+'/'+filename)
            additional += "add_files -fileset constrs_1 -norecurse {}/{}\n".format(p, filename)
            additional += "set_property PROCESSING_ORDER {} [get_files {}/{}]\n".format(ct, p, filename)
        additional += "ipx::merge_project_changes files [ipx::current_core]"
    return additional


def mkVivado(cli):
    ippath = "{cwd}/ip/{projectname}".format(projectname=cli.projectname,cwd=os.getcwd())
    srcpath = "{ippath}/src".format(ippath=ippath)
    inclpath = "{ippath}/src".format(ippath=ippath)
    constraintpath = "{ippath}/constraints".format(ippath=ippath)
    constraints = parseConstraints(cli.constraints)
    includefiles = []
    for path in cli.includes:
        if path.endswith('.v') or path.endswith('.h'):
            includefiles.append(path)
        else:
            for filename in glob.glob(os.path.join(path, '*.v')):
                includefiles.append(filename)

    includes = ['{ippath}/src/{file}'.format(ippath=ippath, file=os.path.basename(x)) for x in includefiles]
    tmpdir = "{cwd}/tmp".format(cwd=os.getcwd())
    print("Creating project with files in {}".format(cli.verilog_dir[0]))
    for path in cli.verilog_dir:
        if not os.path.exists(path):
            print("Cant find {}".format(path))
            return
    if not os.path.exists(srcpath):
        os.makedirs(srcpath)
    else:
        print("{} already exists.".format(srcpath))
        return

    if not os.path.exists(tmpdir):
        os.makedirs(tmpdir)

    copyVerilog(cli.verilog_dir, srcpath, cli.exclude)
    if cli.includes:
        copyVerilog(cli.includes, inclpath, cli.exclude)
    copyNGC(cli.verilog_dir, srcpath, cli.exclude)
    copyBSVVerilog(cli.bluespec_dir, srcpath)
    additional = "\n".join(cli.additional)
    additional += '\n'

    additional += processConstraints(constraints, constraintpath)

    used = executeVivado(createNewProject, cli.vendor, cli.projectname, ippath, tmpdir, cli.topModule, additional, includes)
    used_fullpath = []
    usedNGC = []
    for usedFile in used:
        base_file, ext = os.path.splitext(usedFile)
        used_fullpath.append("{}/src/{}".format(ippath, os.path.basename(usedFile)))
        ngcFile = base_file + ".ngc"
        if os.path.exists(ngcFile):
            usedNGC += [base_file + ".ngc"]

    used = used_fullpath + usedNGC
    removeUnused(used, srcpath)

commands = {'mkVivado':mkVivado}

def find_bluespec():
    pattern = "Bluespec directory: (.*)"
    t = subprocess.Popen("bsc -help", shell=True, stdout=subprocess.PIPE).stdout.read()
    s = t.decode()
    for l in s.splitlines():
        m = re.match(pattern, l)
        if m:
            return m.group(1)
    else:
        return ''


def main():
    parser = argparse.ArgumentParser(description='Tools for BSV developers.')
    parser.add_argument('base_dir', type=str)
    parser.add_argument('command', type=str, choices=commands.keys())
    parser.add_argument('projectname', type=str)
    parser.add_argument('topModule', type=str)
    parser.add_argument('--verilog_dir', nargs='+', default="verilog", type=str)
    parser.add_argument('--vendor', default=vendor, type=str)
    parser.add_argument('--bluespec_dir', default=os.getenv('BLUESPECDIR', find_bluespec()), type=str)
    parser.add_argument('--exclude', nargs='+', default="", type=str)
    parser.add_argument('--additional', nargs='+', default="", type=str)
    parser.add_argument('--includes', nargs='+', default="", type=str)
    parser.add_argument('--constraints', nargs='+', default="", type=str)

    cli = parser.parse_args()

    if cli.bluespec_dir == '':
        print("BLUESPEC_DIR is missing and could not be determined.")
        sys.exit(1)

    commands[cli.command](cli)

if __name__ == '__main__':
    main()
