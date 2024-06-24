#!/usr/bin/env python3
# utils.py - helper function module


import re
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


def get_mouse_alias_and_model():
    """
    Parses the ratbagctl short name of the connected mouse and the mouse model
        Returns:
            (alias, model)
            alias (str): the ratbagctl name of the mouse, ex. "sleeping-puppy"
            model (str): the model short name/number of the mouse, ex. "G403"
    """
    rbc_out = get_bash_stdout("ratbagctl list")
    mouse_re = re.compile(r"([a-z-]+):.*(G\d{3}|G Pro).*")
    mouse_mo = mouse_re.match(rbc_out)
    alias = mouse_mo.group(1).lower()
    model = mouse_mo.group(2).lower()
    return (alias, model)


def print_list_or_help_msg():
    """
    Prints generic instructions in case of an invalid command
    """
    print(f"Run 'lgmpm.py --list' for a list of saved profiles")
    print(" or 'lgmpm.py --help' for help")
    return
