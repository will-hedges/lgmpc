#!/usr/bin/env python3
# lgmp.py - Logitech G Mouse Profiler
#   a script to cycle Logitech G mouse profiles with ratbagctl

import subprocess

from mouse import Mouse


def get_bash_stdout(cmd_str):
    """
    Runs a bash command and returns the decoded standard output
        Params:
            cmd_str (str): a bash command, ex. "ratbagctl list"
        Returns:
            rbc_out (str): the decoded standard output (stdout) of cmd_str
    """
    cmd_lst = [c.strip() for c in cmd_str.split(" ")]
    rbc_out = subprocess.run(cmd_lst, stdout=subprocess.PIPE).stdout.decode()
    return rbc_out


def main():
    mouse = Mouse()
    mouse.cycle_profile()
    return


if __name__ == "__main__":
    main()
