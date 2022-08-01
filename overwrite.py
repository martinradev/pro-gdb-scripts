import gdb

class Write_N_Bytes(gdb.Command):
  def __init__(self):
    super(Write_N_Bytes, self).__init__("write_n_bytes", gdb.COMMAND_DATA)

  def invoke(self, arg, from_tty):
    tokens = arg.split(" ")
    if len(tokens) != 3:
      print("Error. Example usage: write_n_bytes QEMU_VA LEN BYTE")
    addr = int(tokens[0], 16) 
    l = int(tokens[1], 16) 
    by = int(tokens[2], 16).to_bytes(1, 'little') * l 

    th = gdb.inferiors()[0]
    th.write_memory(addr, by)

class Write_String(gdb.Command):
  def __init__(self):
    super(Write_String, self).__init__("write_string", gdb.COMMAND_DATA)

  def invoke(self, arg, from_tty):
    i = arg.find(" ")
    addr = int(arg[: i], 16)
    s = arg[i + 1:].encode("ascii")
    s += b"\x00"

    th = gdb.inferiors()[0]
    th.write_memory(addr, s)

Write_String()
Write_N_Bytes()
