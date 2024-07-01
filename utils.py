#!/usr/bin/env python3
# utils.py - helper function module for lgmpm.py

import argparse
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


def mouse_arg_parser():
    """
    Uses argparse to parse CLI arguments passed to the program
        Returns:
            argparse.Namespace
    """
    parser = argparse.ArgumentParser(
        description="manages profiles for Logitech G mice using ratbagctl",
    )
    parser.add_argument(
        "profile_name",
        nargs="?",
        type=str,
        default="default",
        help="the name of the profile",
    )
    parser.add_argument(
        "-a",
        "--active",
        help="make <profile_name> the active profile",
        action="store_true",
    )
    parser.add_argument(
        "-c",
        "--cycle",
        help="cycle (up) to the next stored profile, if one exists",
        action="store_true",
    )
    parser.add_argument(
        "-d",
        "--delete",
        help="delete <profile_name>",
        action="store_true",
    )
    parser.add_argument(
        "-l",
        "--list",
        help="list all saved profiles for the connected mouse",
        action="store_true",
    )
    parser.add_argument(
        "-n",
        "--new",
        help="create a new profile with called <profile_name>",
        action="store_true",
    )
    parser.add_argument(
        "-s",
        "--show",
        help="show the saved settings for <profile_name>",
        action="store_true",
    )
    parser.add_argument(
        "-u",
        "--update",
        help="update <profile_name> with the current mouse settings",
        action="store_true",
    )

    return parser.parse_args()


def print_list_msg():
    print("See 'lgmpm.py --list' for a list of saved profiles")
    return


def print_help_msg():
    print("See 'lgmpm.py --help' for help")
    return
