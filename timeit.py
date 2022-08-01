import gdb
import argparse
import time

class Timeit(gdb.Command):
  def __init__(self):
    super(Timeit, self).__init__("timeit", gdb.COMMAND_DATA)

  def invoke(self, arg, from_tty):
    if arg == None or arg == "":
        print("Provide a command")
        return

    cmd = arg
    t1 = time.time()
    gdb.execute(arg)
    t2 = time.time()
    elapsed = t2 - t1
    
    print(f"Command '{cmd}' took {elapsed} secs")

Timeit()
