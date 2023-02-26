import gdb
import argparse
import tempfile
import subprocess

def save_to_temp_files(data1, data2):
    names = []
    for d in [data1, data2]:
        f = tempfile.NamedTemporaryFile(delete=False)
        f.write(d)
        f.close()
        orig = f.name
        f = tempfile.NamedTemporaryFile(delete=False)
        f.close()
        subprocess.run(["xxd", orig, f.name], stdout=subprocess.PIPE)
        names.append(f.name)
    return names

class Snapshot:
    def __init__(self, name, va, extent, memory):
        self.name = name
        self.va = va
        self.extent = extent
        self.memory = memory

class SnapshotMemoryCommand(gdb.Command):
    def __init__(self):
        super(SnapshotMemoryCommand, self).__init__("snap", gdb.COMMAND_USER)

        # Define the argument parser
        self.parser = argparse.ArgumentParser(prog='snap',
            description='Take a snapshot of a memory region and store it in a hashtable',
            epilog='Example: snap --mem --tag mykey --range 0xff0000 0x1000')
        self.parser.add_argument('-m', '--mem', action='store_true', help='take a memory snapshot')
        self.parser.add_argument('-t', '--tag', type=str, help='the keyname to use for the snapshot')
        self.parser.add_argument('-r', '--range', nargs=2, metavar=('addr', 'length'),
            help='the memory region to snapshot, specified as <addr> <length>')
        self.parser.add_argument('-e', '--heap', action='store_true', help='Take snapshot of heap')
        self.parser.add_argument('-d', '--diff', nargs=2, type=str, help='diff two snapshots')
        self.parser.add_argument('-o', '--output', nargs=1, type=str, help='output to a file')

        self.snapshots = {}

    def save_snapshot(self, tag, addr, length):
        memory = gdb.selected_inferior().read_memory(addr, length)
        self.snapshots[tag] = Snapshot(tag, addr, length, memory)
        print(f"Snapshot taken with tag '{tag}'")

    def diff_snapshots(self, key1, key2):
        snap1 = self.snapshots[key1]
        if not snap1:
            raise Exception(f"Did not find {key1}")
        assert(snap1.name == key1)
        snap2 = self.snapshots[key2]
        if not snap2:
            raise Exception(f"Did not find {key2}")
        assert(snap2.name == key2)

        tmp1, tmp2 = save_to_temp_files(snap1.memory, snap2.memory)
        print(f"Saved to temporary files '{tmp1}' and '{tmp2}'")

        diff = subprocess.run(["colordiff", "-y", tmp1, tmp2], stdout=subprocess.PIPE).stdout.decode("ascii")

        n = 120
        print(f"Delta between [0x{hex(snap1.va)},+0x{hex(snap1.extent)}) and [0x{hex(snap2.va)},+0x{hex(snap2.extent)})")
        print("-" * n)
        print(diff)
        print("-" * n)

    def handle_command(self, args):
        if args.mem and args.tag and args.range:
            addr = int(args.range[0], 16)
            length = int(args.range[1], 16)
            keyname = args.tag
            return self.save_snapshot(keyname, addr, length)
        if args.heap:
            keyname = args.tag if args.tag else "heap"
            pid = gdb.execute("pid", to_string=True)[:-1]
            maps = subprocess.run(["cat", f"/proc/{pid}/maps"], stdout=subprocess.PIPE).stdout.decode("ascii")
            heap_range = None
            for line in maps.split("\n"):
                if "heap" in line:
                    tokens = line.split(" ")
                    start, end = tokens[0].split("-")
                    heap_range = (int(start, 16), int(end, 16))
                    break
            if not heap_range:
                print("Failed to find heap range")
                print(f"Maps is:\n{maps}")
                return
            return self.save_snapshot(keyname, heap_range[0], heap_range[1] - heap_range[0])
        elif args.diff:
            key1 = args.diff[0]
            key2 = args.diff[1]
            return self.diff_snapshots(key1, key2)
        else:
            self.parser.print_help()
            return


    def invoke(self, args, from_tty):
        # Parse the arguments
        try:
            args = self.parser.parse_args(gdb.string_to_argv(args))
        except SystemExit:
            return

        stdout = sys.stdout
        try:
            if args.output:
                sys.stdout = open(args.output[0], "w+")
            self.handle_command(args)
        except Exception as e:
            print(f"Failed to run command: {e}")
        finally:
            if sys.stdout:
                sys.stdout.close()
            sys.stdout = stdout

SnapshotMemoryCommand()
