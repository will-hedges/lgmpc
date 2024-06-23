#!/usr/bin/env python3
# mouse.py - a Python class representing a Logitech G mouse

import json
from pathlib import Path
import pickle
import subprocess

from mouseprofile import MouseProfile
from utils import get_mouse_alias_and_model


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


def print_list_or_help_msg():
    print(f"Run 'lgmpm.py --list' for a list of saved profiles")
    print("\tor 'lgmpm.py --help' for help")
    return


def save_status(Mouse):
    mouse_data = {
        "last_run_profile": Mouse.last_run_profile,
        "profiles": Mouse.profiles,
    }
    with open(Mouse.model_json, "w") as jf:
        json.dump(mouse_data, jf, indent=2)


class Mouse:
    """
    A class to represent a Logitech G mouse

        Attrs:
            alias (str): the ratbagctl short name of the mouse
            model (str): the Logitech model name/number of the mouse
            button_count (int): the number of buttons the mouse has
            folder (Path): the dir containing profile scripts and pickle file for the mouse
            profiles (dict): a dict of dicts containing the information for each profile
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
        # catch if the file doesn't exist yet, or is blank
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            # create the file
            model_json_fp.touch()
            # create the "default" profile
            mp = MouseProfile()
            # create a dict that represents the mouse and the profiles
            mouse_data = {}
            # set the last run profile name as 'default'
            last_run_profile = mp.name
            mouse_data["last_run_profile"] = last_run_profile
            mouse_data["profiles"] = {}
            # initialize a dict of profiles with default being the only entry
            #   the key should be "default"
            mouse_data["profiles"][mp.name] = mp.__dict__
            # dump the new mouse model data to file
            with open(model_json_fp, "w") as jf:
                json.dump(mouse_data, jf, indent=2)

        self.alias = alias
        self.model = model
        self.model_json = model_json_fp
        self.last_run_profile = mouse_data["last_run_profile"]
        self.profiles = mouse_data["profiles"]
        return

    def add_profile(self, profile_name, profile_dict):
        """
        Adds a new profile to self.profiles
        Updates the last run profile
        And saves the current status to the model json
        """
        # show an error message if the profile already exists:
        if profile_name in self.profiles.keys():
            print(f"{self.model.upper()} profile '{profile_name}' already exists")
            print("Update it with 'lgmpm.py --update'")
            print_list_or_help_msg()
        else:
            self.profiles[profile_name] = profile_dict
            self.last_run_profile = profile_name
            save_status(self)
        return

    def list_profiles(self):
        return

    def show_profile(self):
        return

    def write_profile(self, profile_name):
        # TODO rename this and the flag
        try:
            mp = MouseProfile(name=profile_name, attrs=self.profiles[profile_name])
            mp.run()
        except KeyError:
            print(f"No stored {self.model.upper()} profile '{profile_name}'")
            print_list_or_help_msg()

        return

    def update_profile(self, profile_name, profile_dict):
        """
        Updates an existing saved profile with the current mouse settings
        Updates the last run profile
        And saves the current status to the model's json
        """
        try:
            self.profiles[profile_name].update(profile_dict)
            self.last_run_profile = profile_name
            save_status(self)
        except KeyError:
            print(f"Could not find {self.model.upper()} profile '{profile_name}'")
            print_list_or_help_msg()
        return

    def delete_profile(self, profile_name):
        try:
            del self.profiles[profile_name]
        except KeyError:
            print(f"The profile {profile_name} does not exist for this mouse.")
            print_list_or_help_msg()

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


def main():
    mouse = Mouse()
    return mouse


if __name__ == "__main__":
    main()
