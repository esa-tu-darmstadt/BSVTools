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
    for intf in intf_list_resolved:
        if intf not in available_interfaces:
            raise NameError("Interface '{}' invalid, supported interfaces are 'tapasco axis {}'.".format(intf, " ".join(available_interfaces.keys())))
        else:
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
                join_intf.rtl_interface_def.append(i)
            for i in intf.rtl_module_inst:
                join_intf.rtl_module_inst.append(i)
            for i in intf.rtl_rules:
                join_intf.rtl_rules.append(i)
            for i in intf.rtl_interface_connections:
                join_intf.rtl_interface_connections.append(i)
            for i in intf.dut_imports:
                import_str = "import " + i + " :: *;";
                if import_str not in join_intf.dut_imports:
                    join_intf.dut_imports.append(import_str)
            for i in intf.dut_instances:
                join_intf.dut_instances.append(i)
            for i in intf.dut_connections:
                join_intf.dut_connections.append(i)
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

class Interrupt(Interface):
    def __init__(self):
        super().__init__()
        self.rtl_imports = ["DReg"]
        self.rtl_interface_def = ["(* always_ready *) method Bool interrupt();"]
        self.rtl_module_inst = ["Reg#(Bool) interruptDReg <- mkDReg(False);"]
        self.rtl_interface_connections = ["method Bool interrupt = interruptDReg;"]

class AXI4StreamMaster(Interface):
    def __init__(self):
        super().__init__()
        self.libraries = [
            "https://github.com/esa-tu-darmstadt/BlueLib.git",
            "https://github.com/esa-tu-darmstadt/BlueAXI.git",
        ]
        self.rtl_imports = ["BlueAXI"]
        self.rtl_typedefs = ["typedef 64 AXIS_DATA_WIDTH;"]
        self.rtl_interface_def = ["interface AXI4_Stream_Wr_Fab#(AXIS_DATA_WIDTH, 0) m_axis;"]
        self.rtl_module_inst = ["let m_axis_inst <- mkAXI4_Stream_Wr(2);"]
        self.rtl_interface_connections = ["interface m_axis = m_axis_inst.fab;"]
        self.dut_imports = ["BlueAXI", "Connectable"]
        self.dut_instances = ["AXI4_Stream_Rd#(AXIS_DATA_WIDTH, 0) s_axis_inst <- mkAXI4_Stream_Rd(2);"]
        self.dut_connections = ["mkConnection(dut.m_axis, s_axis_inst.fab);"]

class AXI4StreamSlave(Interface):
    def __init__(self):
        super().__init__()
        self.libraries = [
            "https://github.com/esa-tu-darmstadt/BlueLib.git",
            "https://github.com/esa-tu-darmstadt/BlueAXI.git",
        ]
        self.rtl_imports = ["BlueAXI"]
        self.rtl_typedefs = ["typedef 64 AXIS_DATA_WIDTH;"]
        self.rtl_interface_def = ["interface AXI4_Stream_Rd_Fab#(AXIS_DATA_WIDTH, 0) s_axis;"]
        self.rtl_module_inst = ["let s_axis_inst <- mkAXI4_Stream_Rd(2);"]
        self.rtl_interface_connections = ["interface s_axis = s_axis_inst.fab;"]
        self.dut_imports = ["BlueAXI", "Connectable"]
        self.dut_instances = ["AXI4_Stream_Wr#(AXIS_DATA_WIDTH, 0) m_axis_inst <- mkAXI4_Stream_Wr(2);"]
        self.dut_connections = ["mkConnection(m_axis_inst.fab, dut.s_axis);"]

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
            "(* prefix=\"M_AXI\" *) interface AXI4_Master_Rd_Fab#(AXI_ADDR_WIDTH, AXI_DATA_WIDTH, AXI_ID_WIDTH, AXI_USER_WIDTH) m_rd;",
            "(* prefix=\"M_AXI\" *) interface AXI4_Master_Wr_Fab#(AXI_ADDR_WIDTH, AXI_DATA_WIDTH, AXI_ID_WIDTH, AXI_USER_WIDTH) m_wr;",
        ]
        self.rtl_module_inst = [
            "let m_rd_inst <- mkAXI4_Master_Rd(1, 1, True);",
            "let m_wr_inst <- mkAXI4_Master_Wr(1, 1, 1, True);",
        ]
        self.rtl_interface_connections = [
            "interface m_rd = m_rd_inst.fab;",
            "interface m_wr = m_wr_inst.fab;",
        ]
        self.dut_imports = ["BlueAXI", "Connectable"]
        self.dut_instances = [
            "AXI4_Slave_Rd#(AXI_ADDR_WIDTH, AXI_DATA_WIDTH, AXI_ID_WIDTH, AXI_USER_WIDTH) s_axi_rd_inst <- mkAXI4_Slave_Rd(2, 2);",
            "AXI4_Slave_Wr#(AXI_ADDR_WIDTH, AXI_DATA_WIDTH, AXI_ID_WIDTH, AXI_USER_WIDTH) s_axi_wr_inst <- mkAXI4_Slave_Wr(2, 2, 2);",
        ]
        self.dut_connections = [
            "mkConnection(dut.m_rd, s_axi_rd_inst.fab);",
            "mkConnection(dut.m_wr, s_axi_wr_inst.fab);",
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
            "(* prefix=\"S_AXI\" *) interface AXI4_Slave_Rd_Fab#(AXI_ADDR_WIDTH, AXI_DATA_WIDTH, AXI_ID_WIDTH, AXI_USER_WIDTH) s_rd;",
            "(* prefix=\"S_AXI\" *) interface AXI4_Slave_Wr_Fab#(AXI_ADDR_WIDTH, AXI_DATA_WIDTH, AXI_ID_WIDTH, AXI_USER_WIDTH) s_wr;",
        ]
        self.rtl_module_inst = [
            "let s_rd_inst <- mkAXI4_Slave_Rd(2, 2);",
            "let s_wr_inst <- mkAXI4_Slave_Wr(2, 2, 2);",
        ]
        self.rtl_interface_connections = [
            "interface s_rd = s_rd_inst.fab;",
            "interface s_wr = s_wr_inst.fab;",
        ]
        self.dut_imports = ["BlueAXI", "Connectable"]
        self.dut_instances = [
            "AXI4_Master_Rd#(AXI_ADDR_WIDTH, AXI_DATA_WIDTH, AXI_ID_WIDTH, AXI_USER_WIDTH) m_axi_rd_inst <- mkAXI4_Master_Rd(2, 2, False);",
            "AXI4_Master_Wr#(AXI_ADDR_WIDTH, AXI_DATA_WIDTH, AXI_ID_WIDTH, AXI_USER_WIDTH) m_axi_wr_inst <- mkAXI4_Master_Wr(2, 2, 2, False);",
        ]
        self.dut_connections = [
            "mkConnection(m_axi_rd_inst.fab, dut.s_rd);",
            "mkConnection(m_axi_wr_inst.fab, dut.s_wr);",
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
            "(* prefix=\"S_AXI_LITE\" *) interface AXI4_Lite_Slave_Rd_Fab#(AXI_SLAVE_ADDR_WIDTH, AXI_SLAVE_DATA_WIDTH) s_lite_rd;",
            "(* prefix=\"S_AXI_LITE\" *) interface AXI4_Lite_Slave_Wr_Fab#(AXI_SLAVE_ADDR_WIDTH, AXI_SLAVE_DATA_WIDTH) s_lite_wr;",
        ]
        self.rtl_module_inst = [
            "Reg#(Bool) start <- mkReg(False);",
            "Reg#(Bit#(AXI_SLAVE_DATA_WIDTH)) result <- mkReg(0);",
            "Reg#(Bit#(AXI_SLAVE_DATA_WIDTH)) arg0 <- mkReg(0);",
            "List#(RegisterOperator#(axiAddrWidth, AXI_SLAVE_DATA_WIDTH)) operators = Nil;",
            "operators = registerHandler('h00, start, operators);",
            "operators = registerHandler('h10, result, operators);",
            "operators = registerHandler('h20, arg0, operators);",
            "let s_lite_inst <- mkGenericAxi4LiteSlave(operators, 1, 1);",
        ]
        self.rtl_interface_connections = [
            "interface s_lite_rd = s_lite_inst.s_rd;",
            "interface s_lite_wr = s_lite_inst.s_wr;",
        ]
        self.dut_imports = ["BlueAXI", "Connectable"]
        self.dut_instances = [
            "AXI4_Lite_Master_Wr#(AXI_SLAVE_ADDR_WIDTH, AXI_SLAVE_DATA_WIDTH) m_axi_lite_wr_inst <- mkAXI4_Lite_Master_Wr(16);",
            "AXI4_Lite_Master_Rd#(AXI_SLAVE_ADDR_WIDTH, AXI_SLAVE_DATA_WIDTH) m_axi_lite_rd_inst <- mkAXI4_Lite_Master_Rd(16);",
        ]
        self.dut_connections = [
            "mkConnection(m_axi_lite_rd_inst.fab, dut.s_lite_rd);",
            "mkConnection(m_axi_lite_wr_inst.fab, dut.s_lite_wr);",
        ]

available_interfaces = {
    'interrupt': Interrupt(),
    'axis-master': AXI4StreamMaster(),
    'axis-slave': AXI4StreamSlave(),
    'axi-master': AXI4MMMaster(),
    'axi-slave': AXI4MMSlave(),
    'axi-lite-slave': AXI4MMLiteSlave(),
}