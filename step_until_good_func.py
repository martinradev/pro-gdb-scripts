import gdb
import argparse
from enum import Enum

class Mode(Enum):
    SINGLE = 0,
    RECORD = 1,
    NONE = 2

class step_until_func(gdb.Command):
    def __init__(self):
        super(step_until_func, self).__init__("step_until_func", gdb.COMMAND_DATA)

    def write(self, str):
        self.file.write(str + "\n")

    def find_register_in_trail_and_print_info(self, trail, reg):
        self.write("Possible occurrences:")
        for item in trail:
            disassembly = item[1]
            if reg in disassembly:
                self.write(disassembly)

    def finalize(self):
        self.file.close()

    def invoke(self, arg, from_tty):
        args = arg.split(" ")
        mode = Mode.NONE
        if len(args) == 2:
            if args[0] != "single":
                print("error: invalid arg")
                return
            mode = Mode.SINGLE
        elif len(args) == 3:
            if args[0] != "record":
                print("Error: record output_file size")
                return
            mode = Mode.RECORD
        else:
            print("error")
            return
        n = int(args[1])
        max_instruction_trail_size = 32
        instruction_trail = []
        self.file = open(args[0], "w")
        if self.file == None:
            print("failed to open file", args[0])
            return
        try:
            for u in range(n):
                res = gdb.execute("x /i $rip", to_string = True)
                instruction = res.split(":")[1]
                if "call" in instruction:
                    registers = ["rax", "rbx", "rcx", "rdx", "rsp", "rdi", "rsi", "rbp"]
                    for u in range(8, 16):
                        registers.append("r" + str(u))
                    for reg in registers:
                        if reg in instruction:
                            self.write(res)
                            self.find_register_in_trail_and_print_info(instruction_trail, reg)
                            if mode == Mode.SINGLE:
                                return
                if len(instruction_trail) >= max_instruction_trail_size:
                    instruction_trail.pop(0)
                rip = int(gdb.parse_and_eval("$rip").cast(gdb.lookup_type("unsigned long")))
                instruction_trail.append((rip, res))
                gdb.execute("si")
        except Exception as e:
            print(e)
            pass
        self.finalize()

step_until_func()
