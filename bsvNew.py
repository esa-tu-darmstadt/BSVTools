#!/usr/bin/env python3

import argparse, os, sys
from bsvAdd import create_machine_file

def dir_path(string):
    if os.path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)

def is_dir_empty(path):
    if not os.listdir(path):
        return True
    else:
        return False

def is_legal_name(project_name):
    keywords = ['Action', 'ActionValue']
    if '-' in project_name or project_name in keywords:
        return False
    else:
        return True

def create_directories(path, test_dir):
    print("Creating base directories.")
    os.mkdir("{}/src".format(path))
    if test_dir:
        os.mkdir("{}/test".format(path))
    os.mkdir("{}/libraries".format(path))

makefile_temp = """###
# DO NOT CHANGE
###
TOP_MODULE=mk{0}
TESTBENCH_MODULE=mkTestbench
IGNORE_MODULES=mkTestbench mkTestsMainTest
MAIN_MODULE={0}
TESTBENCH_FILE={1}/Testbench.bsv
{2}

# Initialize
-include .bsv_tools
ifndef BSV_TOOLS
$(error BSV_TOOLS is not set (Check .bsv_tools or specify it through the command line))
endif
VIVADO_ADD_PARAMS := ''
CONSTRAINT_FILES := ''
EXTRA_BSV_LIBS:=
EXTRA_LIBRARIES:=
RUN_FLAGS:=

PROJECT_NAME={0}

ifeq ($(RUN_TEST),)
RUN_TEST=TestsMainTest
endif

# Default flags
EXTRA_FLAGS=-D "RUN_TEST=$(RUN_TEST)" -D "TESTNAME=mk$(RUN_TEST)"
EXTRA_FLAGS+=-show-schedule -D "BSV_TIMESCALE=1ns/1ps -keep-fires"

###
# User configuration
###

# Comment the following line if -O3 should be used during compilation
# Keep uncommented for short running simulations
CXX_NO_OPT := 1

# Any additional files added during compilation
# For instance for BDPI or Verilog/VHDL files for simulation
# CPP_FILES += $(current_dir)/src/mem_sim.cpp

# Custom defines added to compile steps
# EXTRA_FLAGS+=-D "BENCHMARK=1"

# Flags added to simulator execution
# RUN_FLAGS+=-V dump.vcd

# Add additional parameters for IP-XACT generation. Passed directly to Vivado.
# Any valid TCL during packaging is allowed
# Typically used to fix automatic inference for e.g. clock assignments
# VIVADO_ADD_PARAMS += 'ipx::associate_bus_interfaces -busif M_AXI -clock sconfig_axi_aclk [ipx::current_core]'

# Add custom constraint files, Syntax: Filename,Load Order
# CONSTRAINT_FILES += "$(PWD)/constraints/custom.xdc,LATE"

# Do not change: Load libraries such as BlueAXI or BlueLib
ifneq ("$(wildcard $(PWD)/libraries/*/*.mk)", "")
include $(PWD)/libraries/*/*.mk
endif

# Do not change: Include base makefile
include $(BSV_TOOLS)/scripts/rules.mk
"""

def create_makefile(path, project_name, test_dir):
    print("Creating makefile")
    dir = 'src' if not test_dir else 'test'
    test_var = '' if not test_dir else 'TEST_DIR=$(PWD)/test'
    with open("{}/Makefile".format(path), "w") as f:
        f.write(makefile_temp.format(project_name, dir, test_var))

gitignore = """.deps
.bsv_tools
build
"""

def create_gitignore(path):
    print("Creating gitignore")
    with open("{}/.gitignore".format(path), "w") as f:
        f.write(gitignore)

top_module_temp = """package {0};

interface {0};
// Add custom interface definitions
endinterface

module mk{0}({0});

    rule doNothing;
        $display("Hello World!");
    endrule

endmodule

endpackage
"""

testbench_temp = """package Testbench;
    import Vector :: *;
    import StmtFSM :: *;

    import TestHelper :: *;

    // Project Modules
    import `RUN_TEST :: *;

    typedef 1 TestAmount;

    (* synthesize *)
    module [Module] mkTestbench();
        Vector#(TestAmount, TestHandler) testVec;
        testVec[0] <- `TESTNAME ();

        Reg#(UInt#(32)) testCounter <- mkReg(0);
        Stmt s = {
            seq
                for(testCounter <= 0;
                    testCounter < fromInteger(valueOf(TestAmount));
                    testCounter <= testCounter + 1)
                seq
                    testVec[testCounter].go();
                    await(testVec[testCounter].done());
                endseq
            endseq
        };
        mkAutoFSM(s);
    endmodule

endpackage
"""

testhelper_temp = """package TestHelper;
    interface TestHandler;
        method Action go();
        method Bool done();
    endinterface
endpackage
"""

testmain_temp = """package TestsMainTest;
    import StmtFSM :: *;
    import TestHelper :: *;
    import {0} :: *;

    (* synthesize *)
    module [Module] mkTestsMainTest(TestHandler);

        {0} dut <- mk{0}();

        Stmt s = {{
            seq
                $display("Hello World from the testbench.");
            endseq
        }};
        FSM testFSM <- mkFSM(s);

        method Action go();
            testFSM.start();
        endmethod

        method Bool done();
            return testFSM.done();
        endmethod
    endmodule

endpackage
"""

def create_base_src(path, project_name, test_dir):
    print("Creating main module")
    with open("{}/src/{}.bsv".format(path, project_name), "w") as f:
        f.write(top_module_temp.format(project_name))
        
    dir = 'src' if not test_dir else 'test'

    with open("{}/{}/Testbench.bsv".format(path, dir), "w") as f:
        f.write(testbench_temp)

    with open("{}/{}/TestsMainTest.bsv".format(path, dir), "w") as f:
        f.write(testmain_temp.format(project_name))

    with open("{}/{}/TestHelper.bsv".format(path, dir), "w") as f:
        f.write(testhelper_temp)

def main():
    parser = argparse.ArgumentParser(description="Create a new BSV project")
    parser.add_argument('--path', type=dir_path, default='./')
    parser.add_argument('project_name')
    parser.add_argument('--test_dir', help='Set in case want to separate in src and test folder', action='store_true')

    args = None
    try:
        args = parser.parse_args()
    except NotADirectoryError as e:
        print("Path has to be a valid directory, got: {}.".format(e))
        sys.exit(1)
    
    if not is_dir_empty(args.path):
        print("Directory {} is not empty. Please run this script in an empty directory.".format(args.path))
        sys.exit(1)

    if not args.project_name[0].isupper():
        print("Project name needs to start with a capital letter. Please chose a different name.")
        sys.exit(1)
    
    if not is_legal_name(args.project_name):
        print("Project name needs to NOT have '-' in the name ant NOT be any special keyword. \nPlease chose a different name")
        sys.exit(1)

    create_directories(args.path, args.test_dir)
    create_machine_file(args.path)
    create_gitignore(args.path)
    create_makefile(args.path, args.project_name, args.test_dir)
    create_base_src(args.path, args.project_name, args.test_dir)

if __name__ == "__main__":
    main()
