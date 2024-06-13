#!/usr/bin/env python3
# lgmp.py - Logitech G Mouse Profiler
#   a script to cycle Logitech G mouse profiles with ratbagctl

import re
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


def get_button_count(alias):
    """
    Gets the # of buttons the connected mouse has
    """
    num_buttons = get_bash_stdout(f"ratbagctl {alias} button count")
    return int(num_buttons)


def main():
    mouse = Mouse()
    return


if __name__ == "__main__":
    main()
