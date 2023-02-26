import gdb
import argparse
import sys
from enum import Enum

class Mode(Enum):
    SINGLE = 0,
    RECORD = 1,
    NONE = 2

class step_until_func(gdb.Command):
    """
        Step-in until gdb sees call/jmp

        -c, --call    until call a register
        -j, --jump    until a jmp
        -n, --number  max number of instructions
        -o, --output  save results to a file

        Example:
        step_until -c -j
    """

    def __init__(self):
        super(step_until_func, self).__init__("step_until", gdb.COMMAND_DATA)
        parser = argparse.ArgumentParser()
        parser.add_argument("-c", "--call", action="store_true")
        parser.add_argument("-j", "--jump", action="store_true")
        parser.add_argument("-o", "--output", nargs=1)
        parser.add_argument("-n", "--number", nargs=1)
        self.parser = parser

    def find_register_in_trail_and_print_info(self, trail, reg):
        self.write("Possible occurrences:")
        for item in trail:
            disassembly = item[1]
            if reg in disassembly:
                self.write(disassembly)

    def handle_single(self, calls, jumps, limit):
        gdb.execute("si")
        res = gdb.execute("x /i $rip", to_string = True)
        instruction = res.split(":")[1]
        if (calls and "call" in instruction) or (jumps and "jmp" in instruction):
            registers = ["rax", "rbx", "rcx", "rdx", "rsp", "rdi", "rsi", "rbp"]
            for u in range(8, 16):
                registers.append("r" + str(u))
            for reg in registers:
                if reg in res:
                    print(res)
                    gdb.execute("x /30i $rip - 0x30")
                    gdb.execute("info registers")
                    return True
        return False

    def handle(self, calls, jumps, limit):
        for u in range(limit):
            if self.handle_single(calls, jumps, limit):
                break

    def invoke(self, arg, from_tty):
        args = None
        try:
            args = self.parser.parse_args(arg.split(" "))
        except:
            print("Failed to parse arguments")
            return None

        if not args.jump and not args.call:
            print("Need to request jump and/or call")
            return None

        trace_calls = args.call
        trace_jump = args.jump
        limit = int(args.number) if args.number else 1024 * 1024 * 1024 * 1024

        saved_stdout = sys.stdout
        output_file = args.output[0] if args.output else None
        if output_file:
            sys.stdout = open(output_file, "w+")

        try:
            self.handle(trace_calls, trace_jump, limit)
        except Exception as e:
            print(f"Failed to handle command: {e}")
        finally:
            sys.stdout = saved_stdout
        return

step_until_func()
