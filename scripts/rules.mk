ifeq ($(BUILDDIR),)
	BUILDDIR=build
endif
SILENTCMD=
ifndef VERBOSE
	SILENTCMD=@
endif

ZIP:=""
ifeq (, $(shell which zip))
$(warning "No zip in $(PATH), make ip will not generate zip file")
else
	ZIP:=$(shell which zip)
endif

OUTFILE?=out
SRCDIR?=$(PWD)/src
BSV=bsc
PWD?=$(shell pwd)
BSV_TOOLS_PY:=$(BSV_TOOLS)/scripts/bsvTools.py
BSV_DEPS:=$(BSV_TOOLS)/scripts/bsvDeps.py

BASH:=$(shell which bash)
RM:=$(shell which rm)
MKDIR:=$(shell which mkdir)

BSV_INCLUDEDIR?=$(PWD)/include

USED_DIRECTORIES := $(BUILDDIR) $(BSV_INCLUDEDIR) $(EXTRA_DIRS)

EMPTY :=
SPACE := $(EMPTY) $(EMPTY)
join-with = $(subst $(SPACE),$1,$(strip $2))

LIBRARIES_BASE = %/Libraries $(SRCDIR) $(EXTRA_BSV_LIBS) $(BSV_INCLUDEDIR)
LIBRARIES=$(call join-with,:,$(LIBRARIES_BASE))

CXXFLAGS:=$(CXXFLAGS_EXTRA)
ifdef CXX_COMPAT
CXXFLAGS += -D_GLIBCXX_USE_CXX11_ABI=0 
endif

ifdef CXX_NO_OPT
CXXFLAGS += -O0
else
CXXFLAGS += -O3
endif

ifndef PARALLEL_SIM_LINK
PARALLEL_SIM_LINK:=8
endif


ifeq ($(SIM_TYPE), VERILOG)
VERILOGDIR=verilog
BASEPARAMS=-verilog -vdir $(BUILDDIR)/$(VERILOGDIR) -vsim modelsim
BASEPARAMS_SIM=-verilog -vdir $(VERILOGDIR) -vsim modelsim
COMPILE_FLAGS=-fdir $(PWD) -simdir $(BUILDDIR) -bdir $(BUILDDIR) -info-dir $(BUILDDIR) -p $(LIBRARIES)
COMPLETE_FLAGS=$(BASEPARAMS) $(COMPILE_FLAGS)
USED_DIRECTORIES += $(BUILDDIR)/$(VERILOGDIR)

ifdef VIVADO_ADD_PARAMS
VIVADO_ADD_PARAMS := --additional $(VIVADO_ADD_PARAMS)
endif

ifdef VIVADO_INCLUDES
VIVADO_INCLUDES := --includes $(VIVADO_INCLUDES)
endif

ifdef CONSTRAINT_FILES
CONSTRAINT_FILES := --constraints $(CONSTRAINT_FILES)
endif

ifdef IGNORE_MODULES
	EXCLUDED_VIVADO := --exclude  $(addsuffix .v, $(IGNORE_MODULES))
endif

ip_clean:
	$(RM) -rf $(BUILDDIR)/ip/$(PROJECT_NAME)
	$(RM) -f $(BUILDDIR)/ip/$(PROJECT_NAME).zip

ip: compile_top ip_clean
	@echo "Creating IP $(PROJECT_NAME)"
	$(SILENTCMD)cd $(BUILDDIR); $(BSV_TOOLS_PY) . mkVivado $(PROJECT_NAME) $(TOP_MODULE) --verilog_dir $(VERILOGDIR) $(VERILOGDIR_EXTRAS) $(EXCLUDED_VIVADO) $(VIVADO_ADD_PARAMS) $(VIVADO_INCLUDES) $(CONSTRAINT_FILES)
ifneq (, $(ZIP))
	$(SILENTCMD)cd $(BUILDDIR)/ip && $(ZIP) -r $(PROJECT_NAME).zip $(PROJECT_NAME)
endif

up_ip: compile_top
	@echo "Updating IP $(PROJECT_NAME)"
	$(SILENTCMD)cd $(BUILDDIR); $(BSV_TOOLS_PY) . upVivado $(PROJECT_NAME) $(TOP_MODULE) $(EXCLUDED_VIVADO) $(VIVADO_ADD_PARAMS)

sim_ip: compile_top

compile_top: | directories
	$(SILENTCMD)$(BSV) -elab -verilog $(COMPLETE_FLAGS) $(BSC_FLAGS) -g $(TOP_MODULE) -u $(SRCDIR)/$(MAIN_MODULE).bsv

else
BASEPARAMS=-sim
BASEPARAMS_SIM=$(BASEPARAMS)
COMPILE_FLAGS=-fdir $(PWD) -simdir $(BUILDDIR) -bdir $(BUILDDIR) -info-dir $(BUILDDIR) -p $(LIBRARIES)
COMPLETE_FLAGS=$(BASEPARAMS) $(COMPILE_FLAGS)
endif

BSC_FLAGS=-cross-info \
          -parallel-sim-link $(PARALLEL_SIM_LINK) \
          $(EXTRA_FLAGS)

ifdef VERBOSE
BSC_FLAGS += -v
endif

SRCS=$(wildcard $(SRCDIR)/*.bsv)
$(shell $(BSV_DEPS) $(SRCDIR) $(BUILDDIR) $(RUN_TEST) > .deps)
include .deps

$(USED_DIRECTORIES):
	$(MKDIR) -p $@

.DEFAULT_GOAL := all
all: sim

directories: $(USED_DIRECTORIES)

compile: | directories
	$(SILENTCMD)$(BSV) -elab $(COMPLETE_FLAGS) $(BSC_FLAGS) -g $(TESTBENCH_MODULE) -u $(TESTBENCH_FILE)

$(BUILDDIR)/$(OUTFILE): compile
	@echo Linking $@...
	$(SILENTCMD)cd $(BUILDDIR); CXXFLAGS="$(CXXFLAGS)" bsc -e $(TESTBENCH_MODULE) -o $(notdir $@) $(BSC_FLAGS) $(BASEPARAMS_SIM) $(addprefix -l , $(EXTRA_LIBRARIES)) $(C_FILES) $(CPP_FILES)
	@echo Linking finished

sim: $(BUILDDIR)/$(OUTFILE)
	@echo Simulating $<
	$(SILENTCMD)cd $(BUILDDIR) && $(BASH) -c './$(OUTFILE) $(RUN_FLAGS) | tee simresult.tmp; (! grep -q "ERROR" simresult.tmp); retVal=$$?; $(RM) simresult.tmp; exit $${retVal}'

clean:
	@echo "Cleaning working files"
	$(SILENTCMD)$(RM) -f $(BUILDDIR)/*.bo
	$(SILENTCMD)$(RM) -f $(BUILDDIR)/*.ba
	$(SILENTCMD)$(RM) -f $(BUILDDIR)/*.o
	$(SILENTCMD)$(RM) -f $(BUILDDIR)/$(OUTFILE)

clean_all: clean
	@echo "Cleaning all files"
	$(SILENTCMD)$(RM) -rf $(BUILDDIR)
