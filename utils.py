#!/usr/bin/env python3
# utils.py - helper function module


import subprocess


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
