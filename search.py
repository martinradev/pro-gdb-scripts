import gdb
import argparse

class Find_Ptr(gdb.Command):
  def __init__(self):
    super(Find_Ptr, self).__init__("find_ptr", gdb.COMMAND_DATA)

  def invoke(self, arg, from_tty):
    tok = arg.split(" ")
    if len(tok) != 4:
        print("Example usage: find_ptr PTR_RANGE_A PTR_RANGE_B SEARCH_RANGE_A SEARCH_RANGE_B")
        return None
    ptr1 = int(tok[0], 16)
    ptr2 = int(tok[1], 16)
    search1 = int(tok[2], 16)
    search2 = int(tok[3], 16)
    
    th = gdb.inferiors()[0]
    mem = th.read_memory(search1, search2-search1)
    for u in range(len(mem) - 8):
        tmp = int.from_bytes(mem[u: u + 8], 'little')
        if tmp >= ptr1 and tmp <= ptr2:
            print(f"Found {hex(tmp)} at addr {hex(search1 + u)}")

class Find_Sim_Ptr(gdb.Command):
  def __init__(self):
    super(Find_Sim_Ptr, self).__init__("find_sim_ptr", gdb.COMMAND_DATA)

  def invoke(self, arg, from_tty):
    tok = arg.split(" ")
    if len(tok) != 3:
        print("Example usage: find_ptr PTR_RANGE_A PTR_RANGE_B PTR")
        return None
    ptr1 = int(tok[0], 16)
    ptr2 = int(tok[1], 16)
    search = int(tok[2], 16)
    
    th = gdb.inferiors()[0]
    mem = th.read_memory(search1, search2-search1)
    for u in range(len(mem) - 8):
        tmp = int.from_bytes(mem[u: u + 8], 'little')
        delta = search ^ tmp
        if (delta & ~0xFFFF) == 0:
            print(f"Found {hex(tmp)} at addr {hex(search1 + u)}")


class Find_Data(gdb.Command):
    def __init__(self, sz):
        super(Find_Data, self).__init__(f"f{sz}", gdb.COMMAND_DATA)
        parser = argparse.ArgumentParser()
        parser.add_argument("-r", type=lambda x: int(x, 0), nargs=2, required=True)
        parser.add_argument("value", type=lambda x: int(x, 0), nargs=1)
        self.parser = parser
        self.size = sz

    def invoke(self, arg, from_tty):
        args = self.parser.parse_args(arg.split())
        start = args.r[0]
        end = args.r[1]
        if start > end:
            print(f"Start {hex(start)} should be less than {hex(end)}.")
            return

        th = gdb.selected_inferior()
        max_block_size = 0x100000
        value_as_bytes = args.value[0].to_bytes(self.size, 'little')
        for block_start in range(start, end, max_block_size):
            sz = min(end - start, max_block_size)
            memory = th.read_memory(block_start, sz).tobytes()
            i = 0
            while True:
                i = memory.find(value_as_bytes, i)
                if i == -1:
                    break
                print(f"Found at {hex(block_start + i)}")
                i = i + 1

Find_Ptr()
Find_Sim_Ptr()
for u in range(1, 9):
    Find_Data(u)
