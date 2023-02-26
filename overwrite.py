import gdb

class Write_N_Bytes(gdb.Command):
    """
        write_n_bytes QEMU_VA LEN BYTE

        Writes LEN * BYTE at QEMU_VA
        BYTE needs to be in hex

        Example:
        write_n_bytes 0x7ffff0000 0x1000 0x41
    """
    def __init__(self):
        super(Write_N_Bytes, self).__init__("write_n_bytes", gdb.COMMAND_DATA)

    def invoke(self, arg, from_tty):
        tokens = arg.split(" ")
        if len(tokens) != 4:
            print("Error. Example usage: write_n_bytes QEMU_VA LEN BYTE")
            return
        addr = int(tokens[0], 16)
        l = int(tokens[1], 16)
        by = int(tokens[2], 16).to_bytes(1, 'little') * l
        off = int(tokens[3], 16)
        addr = addr + off

        th = gdb.inferiors()[0]
        th.write_memory(addr, by)

class Write_Inf(gdb.Command):
    """
        write_inf QEMU_VA LEN

        Writes an instruction sequence of infinite loops to 'trap' code.
        The written sequence is EB FE

        The LEN is number of bytes, not the number of infinite loop sequences.

        Example:
        write_inf 0x7ffff0000 0x1000
    """
    def __init__(self):
        super(Write_Inf, self).__init__("write_inf", gdb.COMMAND_DATA)

    def invoke(self, arg, from_tty):
        tokens = arg.split(" ")
        if len(tokens) != 2:
            print("Error. Example usage: write_n_bytes QEMU_VA LEN")
            return
        addr = int(tokens[0], 16)
        l = int(tokens[1], 16)
        by = b"\xeb\xfe" * int(l / 2)

        th = gdb.inferiors()[0]
        th.write_memory(addr, by)

class Write_Ud(gdb.Command):
    """
        write_ud QEMU_VA LEN

        Writes an instruction sequence of UD instructions.

        The LEN is number of bytes, not the number of UD instructions.

        Example:
        write_ud 0x7ffff0000 0x1000
    """
    def __init__(self):
        super(Write_Ud, self).__init__("write_ud", gdb.COMMAND_DATA)

    def invoke(self, arg, from_tty):
        tokens = arg.split(" ")
        if len(tokens) != 2:
            print("Error. Example usage: write_n_bytes QEMU_VA LEN")
            return
        addr = int(tokens[0], 16)
        l = int(tokens[1], 16)
        if l % 2 != 0:
            print("Length should be divisible by 2")
            return
        l = int(l / 2)
        th = gdb.inferiors()[0]
        th.write_memory(addr, b"\x0f\x0b" * l)


class Write_String(gdb.Command):
    """
        write_string QEMU_VA STRING

        Write STRING at QEMU_VA

        Example:
        write_ud 0x7ffff0000 hello world
    """
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
Write_Ud()
Write_Inf()
