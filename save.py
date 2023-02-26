import gdb

class DumpMe(gdb.Command):
    """
        Saves va range to a file in binary

        dump_bin file base_va extent

        dump_bin /tmp/file.bin 0x7f00000000 0x1000
    """

    def __init__(self):
        super(DumpMe, self).__init__("dump_bin", gdb.COMMAND_DATA)

    def invoke(self, arg, from_tty):
        tokens = arg.split(" ")
        if len(tokens) != 3:
            print("Error. Example usage: dump_bin FILE QEMU_VA LEN")
            return
        file  = tokens[0]
        addr = int(tokens[1], 16) 
        l = int(tokens[2], 16) 

        th = gdb.inferiors()[0]
        data = th.read_memory(addr, l)
        f = open(file, "wb+")
        f.write(data)
        f.close()

DumpMe()
