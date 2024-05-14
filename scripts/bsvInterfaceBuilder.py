def create_interfaces(intf_list):
    join_intf = Interface()
    if intf_list == None:
        return join_intf
    # resolve aliases
    intf_list_resolved = []
    for i in intf_list:
        if i == "axis":
            intf_list_resolved.append("axis-master")
            intf_list_resolved.append("axis-slave")
        elif i == "tapasco":
            intf_list_resolved.append("axi-lite-slave")
            intf_list_resolved.append("interrupt")
        else:
            intf_list_resolved.append(i)
    # build a dict with all name suffixes or empty for a single occurence of the interface
    intf_names_dict = dict()
    for intf in intf_list_resolved:
        count = intf_list_resolved.count(intf)
        if count == 1:
            intf_names_dict[intf] = ['']
        else:
            names = []
            for i in range(count):
                names.append('_{}'.format(i))
            intf_names_dict[intf] = names
    for intf in intf_list_resolved:
        if intf not in available_interfaces:
            raise NameError("Interface '{}' invalid, supported interfaces are 'tapasco axis {}'.".format(intf, " ".join(available_interfaces.keys())))
        else:
            intf_name = intf_names_dict[intf].pop(0)
            intf = available_interfaces[intf]
            for i in intf.libraries:
                # avoid duplicates
                if i not in join_intf.libraries:
                    join_intf.libraries.append(i)
            for i in intf.rtl_imports:
                # avoid duplicates
                import_str = "import " + i + " :: *;";
                if import_str not in join_intf.rtl_imports:
                    join_intf.rtl_imports.append(import_str)
            for i in intf.rtl_typedefs:
                # avoid duplicates
                if i not in join_intf.rtl_typedefs:
                    join_intf.rtl_typedefs.append(i)
            for i in intf.rtl_interface_def:
                join_intf.rtl_interface_def.append(i.format(name = intf_name))
            for i in intf.rtl_module_inst:
                join_intf.rtl_module_inst.append(i.format(name = intf_name))
            for i in intf.rtl_rules:
                join_intf.rtl_rules.append(i.format(name = intf_name))
            for i in intf.rtl_interface_connections:
                join_intf.rtl_interface_connections.append(i.format(name = intf_name))
            for i in intf.dut_imports:
                import_str = "import " + i + " :: *;";
                if import_str not in join_intf.dut_imports:
                    join_intf.dut_imports.append(import_str)
            for i in intf.dut_instances:
                join_intf.dut_instances.append(i.format(name = intf_name))
            for i in intf.dut_connections:
                join_intf.dut_connections.append(i.format(name = intf_name))
            for i in intf.dut_init:
                join_intf.dut_init.append(i.format(name = intf_name))
            for i in intf.dut_rules:
                join_intf.dut_rules.append(i.format(name = intf_name))
    return join_intf

class Interface:
    def __init__(self):
        self.libraries = []
        self.rtl_imports = []
        self.rtl_typedefs = []
        self.rtl_interface_def = []
        self.rtl_module_inst = []
        self.rtl_rules = []
        self.rtl_interface_connections = []
        self.dut_imports = []
        self.dut_instances = []
        self.dut_connections = []
        self.dut_init = []
        self.dut_rules = []

class Interrupt(Interface):
    def __init__(self):
        super().__init__()
        self.rtl_imports = ["DReg"]
        self.rtl_interface_def = ["(* always_ready *) method Bool interrupt{name}();"]
        self.rtl_module_inst = ["Reg#(Bool) interruptDReg{name} <- mkDReg(False);"]
        self.rtl_interface_connections = ["method Bool interrupt{name} = interruptDReg{name};"]
        self.dut_rules = [
            "rule finishOnInterrupt{name} (dut.interrupt{name});",
            "    $display(\"Interrupt{name} received, finishing simulation\");",
            "    $finish;",
            "endrule",
        ]

class AXI4StreamMaster(Interface):
    def __init__(self):
        super().__init__()
        self.libraries = [
            "https://github.com/esa-tu-darmstadt/BlueLib.git",
            "https://github.com/esa-tu-darmstadt/BlueAXI.git",
        ]
        self.rtl_imports = ["BlueAXI"]
        self.rtl_typedefs = ["typedef 64 AXIS_DATA_WIDTH;"]
        self.rtl_interface_def = ["interface AXI4_Stream_Wr_Fab#(AXIS_DATA_WIDTH, 0) m_axis{name};"]
        self.rtl_module_inst = ["let m_axis_inst{name} <- mkAXI4_Stream_Wr(2);"]
        self.rtl_interface_connections = ["interface m_axis{name} = m_axis_inst{name}.fab;"]
        self.dut_imports = ["BlueAXI", "Connectable"]
        self.dut_instances = ["AXI4_Stream_Rd#(AXIS_DATA_WIDTH, 0) s_axis_inst{name} <- mkAXI4_Stream_Rd(2);"]
        self.dut_connections = ["mkConnection(dut.m_axis{name}, s_axis_inst{name}.fab);"]

class AXI4StreamSlave(Interface):
    def __init__(self):
        super().__init__()
        self.libraries = [
            "https://github.com/esa-tu-darmstadt/BlueLib.git",
            "https://github.com/esa-tu-darmstadt/BlueAXI.git",
        ]
        self.rtl_imports = ["BlueAXI"]
        self.rtl_typedefs = ["typedef 64 AXIS_DATA_WIDTH;"]
        self.rtl_interface_def = ["interface AXI4_Stream_Rd_Fab#(AXIS_DATA_WIDTH, 0) s_axis{name};"]
        self.rtl_module_inst = ["let s_axis_inst{name} <- mkAXI4_Stream_Rd(2);"]
        self.rtl_interface_connections = ["interface s_axis{name} = s_axis_inst{name}.fab;"]
        self.dut_imports = ["BlueAXI", "Connectable"]
        self.dut_instances = ["AXI4_Stream_Wr#(AXIS_DATA_WIDTH, 0) m_axis_inst{name} <- mkAXI4_Stream_Wr(2);"]
        self.dut_connections = ["mkConnection(m_axis_inst{name}.fab, dut.s_axis{name});"]

class AXI4MMMaster(Interface):
    def __init__(self):
        super().__init__()
        self.libraries = [
            "https://github.com/esa-tu-darmstadt/BlueLib.git",
            "https://github.com/esa-tu-darmstadt/BlueAXI.git",
        ]
        self.rtl_imports = ["BlueAXI"]
        self.rtl_typedefs = [
            "typedef 64 AXI_ADDR_WIDTH;",
            "typedef 512 AXI_DATA_WIDTH;",
            "typedef 8 AXI_ID_WIDTH;",
            "typedef 0 AXI_USER_WIDTH;",
        ]
        self.rtl_interface_def = [
            "(* prefix=\"M_AXI{name}\" *) interface AXI4_Master_Rd_Fab#(AXI_ADDR_WIDTH, AXI_DATA_WIDTH, AXI_ID_WIDTH, AXI_USER_WIDTH) m_rd{name};",
            "(* prefix=\"M_AXI{name}\" *) interface AXI4_Master_Wr_Fab#(AXI_ADDR_WIDTH, AXI_DATA_WIDTH, AXI_ID_WIDTH, AXI_USER_WIDTH) m_wr{name};",
        ]
        self.rtl_module_inst = [
            "let m_rd_inst{name} <- mkAXI4_Master_Rd(1, 1, True);",
            "let m_wr_inst{name} <- mkAXI4_Master_Wr(1, 1, 1, True);",
        ]
        self.rtl_interface_connections = [
            "interface m_rd{name} = m_rd_inst{name}.fab;",
            "interface m_wr{name} = m_wr_inst{name}.fab;",
        ]
        self.dut_imports = ["BlueAXI", "Connectable", "BRAM"]
        self.dut_instances = [
            "BRAM2PortBE#(Bit#(63), Bit#(AXI_DATA_WIDTH), TDiv#(AXI_DATA_WIDTH, 8)) bram{name} <- mkBRAM2ServerBE(defaultValue);",
            "BlueAXIBRAM#(AXI_ADDR_WIDTH, AXI_DATA_WIDTH, AXI_ID_WIDTH) s_axi_mem{name} <- mkBlueAXIBRAM(bram{name}.portA);",
        ]
        self.dut_connections = [
            "mkConnection(dut.m_rd{name}, s_axi_mem{name}.rd);",
            "mkConnection(dut.m_wr{name}, s_axi_mem{name}.wr);",
        ]

class AXI4MMSlave(Interface):
    def __init__(self):
        super().__init__()
        self.libraries = [
            "https://github.com/esa-tu-darmstadt/BlueLib.git",
            "https://github.com/esa-tu-darmstadt/BlueAXI.git",
        ]
        self.rtl_imports = ["BlueAXI"]
        self.rtl_typedefs = [
            "typedef 64 AXI_ADDR_WIDTH;",
            "typedef 512 AXI_DATA_WIDTH;",
            "typedef 8 AXI_ID_WIDTH;",
            "typedef 0 AXI_USER_WIDTH;",
        ]
        self.rtl_interface_def = [
            "(* prefix=\"S_AXI{name}\" *) interface AXI4_Slave_Rd_Fab#(AXI_ADDR_WIDTH, AXI_DATA_WIDTH, AXI_ID_WIDTH, AXI_USER_WIDTH) s_rd{name};",
            "(* prefix=\"S_AXI{name}\" *) interface AXI4_Slave_Wr_Fab#(AXI_ADDR_WIDTH, AXI_DATA_WIDTH, AXI_ID_WIDTH, AXI_USER_WIDTH) s_wr{name};",
        ]
        self.rtl_module_inst = [
            "let s_rd_inst{name} <- mkAXI4_Slave_Rd(2, 2);",
            "let s_wr_inst{name} <- mkAXI4_Slave_Wr(2, 2, 2);",
        ]
        self.rtl_interface_connections = [
            "interface s_rd{name} = s_rd_inst{name}.fab;",
            "interface s_wr{name} = s_wr_inst{name}.fab;",
        ]
        self.dut_imports = ["BlueAXI", "Connectable"]
        self.dut_instances = [
            "AXI4_Master_Rd#(AXI_ADDR_WIDTH, AXI_DATA_WIDTH, AXI_ID_WIDTH, AXI_USER_WIDTH) m_axi_rd_inst{name} <- mkAXI4_Master_Rd(2, 2, False);",
            "AXI4_Master_Wr#(AXI_ADDR_WIDTH, AXI_DATA_WIDTH, AXI_ID_WIDTH, AXI_USER_WIDTH) m_axi_wr_inst{name} <- mkAXI4_Master_Wr(2, 2, 2, False);",
        ]
        self.dut_connections = [
            "mkConnection(m_axi_rd_inst{name}.fab, dut.s_rd{name});",
            "mkConnection(m_axi_wr_inst{name}.fab, dut.s_wr{name});",
        ]

class AXI4MMLiteSlave(Interface):
    def __init__(self):
        super().__init__()
        self.libraries = [
            "https://github.com/esa-tu-darmstadt/BlueLib.git",
            "https://github.com/esa-tu-darmstadt/BlueAXI.git",
        ]
        self.rtl_imports = ["BlueAXI"]
        self.rtl_typedefs = [
            "typedef 12 AXI_SLAVE_ADDR_WIDTH;",
            "typedef 64 AXI_SLAVE_DATA_WIDTH;",
        ]
        self.rtl_interface_def = [
            "(* prefix=\"S_AXI_LITE{name}\" *) interface AXI4_Lite_Slave_Rd_Fab#(AXI_SLAVE_ADDR_WIDTH, AXI_SLAVE_DATA_WIDTH) s_lite_rd{name};",
            "(* prefix=\"S_AXI_LITE{name}\" *) interface AXI4_Lite_Slave_Wr_Fab#(AXI_SLAVE_ADDR_WIDTH, AXI_SLAVE_DATA_WIDTH) s_lite_wr{name};",
        ]
        self.rtl_module_inst = [
            "Reg#(Bool) start{name} <- mkReg(False);",
            "Reg#(Bit#(AXI_SLAVE_DATA_WIDTH)) result{name} <- mkReg(0);",
            "Reg#(Bit#(AXI_SLAVE_DATA_WIDTH)) arg0{name} <- mkReg(0);",
            "List#(RegisterOperator#(axiAddrWidth, AXI_SLAVE_DATA_WIDTH)) operators{name} = Nil;",
            "operators{name} = registerHandler('h00, start{name}, operators{name});",
            "operators{name} = registerHandler('h10, result{name}, operators{name});",
            "operators{name} = registerHandler('h20, arg0{name}, operators{name});",
            "let s_lite_inst{name} <- mkGenericAxi4LiteSlave(operators{name}, 1, 1);",
        ]
        self.rtl_interface_connections = [
            "interface s_lite_rd{name} = s_lite_inst{name}.s_rd;",
            "interface s_lite_wr{name} = s_lite_inst{name}.s_wr;",
        ]
        self.dut_imports = ["BlueAXI", "Connectable"]
        self.dut_instances = [
            "AXI4_Lite_Master_Wr#(AXI_SLAVE_ADDR_WIDTH, AXI_SLAVE_DATA_WIDTH) m_axi_lite_wr_inst{name} <- mkAXI4_Lite_Master_Wr(16);",
            "AXI4_Lite_Master_Rd#(AXI_SLAVE_ADDR_WIDTH, AXI_SLAVE_DATA_WIDTH) m_axi_lite_rd_inst{name} <- mkAXI4_Lite_Master_Rd(16);",
        ]
        self.dut_connections = [
            "mkConnection(m_axi_lite_rd_inst{name}.fab, dut.s_lite_rd{name});",
            "mkConnection(m_axi_lite_wr_inst{name}.fab, dut.s_lite_wr{name});",
        ]
        self.dut_rules = [
            "rule dropWrSlaveResp{name};",
            "    let r <- axi4_lite_write_response(m_axi_lite_wr_inst{name});",
            "endrule",
        ]
        self.dut_init = ["axi4_lite_write(m_axi_lite_wr_inst{name}, 'h00, 1);"]

available_interfaces = {
    'interrupt': Interrupt(),
    'axis-master': AXI4StreamMaster(),
    'axis-slave': AXI4StreamSlave(),
    'axi-master': AXI4MMMaster(),
    'axi-slave': AXI4MMSlave(),
    'axi-lite-slave': AXI4MMLiteSlave(),
}

def list_available_interfaces() :
    aliases = ["axis", "tapasco"]
    return aliases + list(available_interfaces.keys())
