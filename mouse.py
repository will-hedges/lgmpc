#!/usr/bin/env python3
# mouse.py - a Python class representing a Logitech G mouse

import json
from pathlib import Path
import pickle
import re
import subprocess

from mouseprofile import MouseProfile
from utils import get_bash_stdout, get_mouse_alias_and_model


def get_button_count(alias):
    """
    Gets the number of buttons on the connected mouse
        Params:
            alias (str): the ratbagctl short name of the connected mouse
        Returns:
            btn_ct (int): the number of buttons the mouse has
    """
    btn_ct = int(get_bash_stdout(f"ratbagctl {alias} button count"))
    return btn_ct


def get_all_shell_scripts_in(fp):
    """
    Creates a list of all the the .sh scripts within a folder

        Params:
            fp (Path): the Path of the mouse model
        Returns:
            profiles (list(Path)): a list of all Paths in fp with the .sh ext
    """
    profile_glob = sorted(fp.glob("*.sh"))
    profiles = [Path(profile) for profile in profile_glob]
    return profiles


# NOTE json may be a better option for serialization here, as you could go
#   in and edit it manually rather than relying on pickle and rb/wb
def get_last_run_profile(fp):
    """
    Pulls in the path of the last set profile from the model.json file
        or creates a json file if it does not already exist

        Params:
            TODO FIXME
            fp (Path): the Path of the mouse model directory
        Returns:
            last_run_profile (str): the name (i.e. key) of the last run profile
    """

    json_path = Path(fp / f"{fp.name}.json")
    try:
        with open(json_path, "rb") as jf:
            last_run_profile = json.load(jf)
    except (FileNotFoundError, EOFError):
        json_path.touch()
        last_run_profile = "default"

    return last_run_profile


def save_last_run_profile(json_fp, profile_name):
    """
    Saves the path of the currently set profile .sh to pickle file
        Params:
            json_fp (Path): the Path to the model.json file
            profile_name (str): the name of the last run profile
    """
    with open(json_fp, "w") as jf:
        pickle.dump(profile_name, jf)
    return


class Mouse:
    """
    A class to represent a Logitech G mouse

        Attrs:
            alias (str): the ratbagctl short name of the mouse
            model (str): the Logitech model name/number of the mouse
            button_count (int): the number of buttons the mouse has
            folder (Path): the dir containing profile scripts and pickle file for the mouse
            profiles (list): a list of Path objects of all the local mouse profile scripts

        Methods:
            cycle_profile TODO
    """

    def __init__(self):
        # try to load from json
        # if no .json, we will make one and set "profiles" and "last_profile" keys
        # should it be one.json or model-specific?
        # I like the simplicity of model-specific personally
        # it will look something like this
        """
        {
            "alias": "singing-gundi",
            "model": "G403",
            "profiles": {
                "default": json.dumps(foo.__dict__),
                "hades": json.dumps(bar.__dict__)
            }
        }
        """
        alias, model = get_mouse_alias_and_model()
        model_json_fp = Path(__file__).parent / "models" / f"{model}.json"
        try:
            with open(model_json_fp, "r") as jf:
                mouse_data = json.load(jf)
        # catch if the file doesn't exist yet
        # or if it was written by another call but ended up blank
        except FileNotFoundError:
            # create the file
            model_json_fp.touch()
            # create the "default" profile
            mp = MouseProfile(alias)
            # create a dict from the mouse_profile attrs
            mp_dict = mp.__dict__
            # create a dict that represents the mouse and the profiles
            mouse_data = {}
            # set the last run profile name as 'default'
            last_profile_name = mp.name
            mouse_data["last_profile_name"] = last_profile_name
            # initialize a list of profiles with default being the only entry
            mouse_data["profiles"] = [mp_dict]
            # dump the new mouse model data to file
            with open(model_json_fp, "w") as jf:
                json.dump(mouse_data, jf, indent=2)

        self.alias = alias
        self.model = model
        self.last_profile_name = mouse_data["last_profile_name"]
        self.profiles = mouse_data["profiles"]
        return

    def cycle_profile(self):
        """
        Cycles through and runs the "next" indexed profile shell script
            then saves the current profile to the pickle file
        """
        last_run_profile = get_last_run_profile(self.folder)
        current_idx = self.profiles.index(last_run_profile)
        try:
            last_run_profile = self.profiles[current_idx + 1]
        except IndexError:
            last_run_profile = self.profiles[0]
        self.last_run_profile = last_run_profile
        # run the new profile script with subprocess
        subprocess.run(["sh", last_run_profile])
        # write out the new profile to pickle
        json_fp = Path(self.folder / f"{self.model}.pickle")
        save_last_run_profile(json_fp, last_run_profile)
        return
