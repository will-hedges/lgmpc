#!/usr/bin/env python3
# mouse.py - a Python class representing a Logitech G mouse

import json
from pathlib import Path

from mouseprofile import MouseProfile
from utils import get_mouse_alias_and_model, print_list_msg, print_help_msg


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
            # initialize a dict of profiles with default being the only entry
            #   the key should be "default"
            mouse_data["profiles"] = {}
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
    
    def save_status(self):
        mouse_data = {
            "last_run_profile": self.last_run_profile,
            "profiles": self.profiles,
        }
        with open(self.model_json, "w") as jf:
            json.dump(mouse_data, jf, indent=2)
        return

    def add_new_profile(self, profile_name, profile_dict):
        """
        Adds a new profile to self.profiles
        Updates the last run profile
        And saves the current status to the model json
        """
        # show an error message if the profile already exists:
        if profile_name in self.profiles.keys():
            print(f"{self.model.upper()} profile '{profile_name}' already exists")
            print("Update it with 'lgmpm.py --update'")
            print_list_msg()
            print_help_msg()
        else:
            self.profiles[profile_name] = profile_dict
            self.last_run_profile = profile_name
            self.save_status()
        return

    def list_profiles(self):
        return

    def show_profile(self):  # TODO shouldn't this be a MouseProfile method?
        return

    def set_active_profile(self, profile_name):
        try:
            mp = MouseProfile(name=profile_name, attrs=self.profiles[profile_name])
            mp.run()
            # set the last active profile
            self.save_status()
        except KeyError:
            print(f"No stored {self.model.upper()} profile '{profile_name}'")
            print_list_msg()
            print_help_msg()

        return

    def update_profile(self, profile_name, profile_dict):
        """
        Updates an existing saved profile with the current mouse settings,
            updates the last run profile,
                and saves the current status to the model's json
        """
        try:
            self.profiles[profile_name].update(profile_dict)
            self.last_run_profile = profile_name
            self.save_status()
        except KeyError:
            print(f"Could not find {self.model.upper()} profile '{profile_name}'")
            print_list_msg()
            print_help_msg()
        return

    def delete_profile(self, profile_name):
        try:
            del self.profiles[profile_name]
        except KeyError:
            print(f"The profile {profile_name} does not exist for this mouse.")
            print_list_msg()
            print_help_msg()

    def cycle_profile(self):
        """
        Cycles through and runs the "next" indexed profile shell script
            then saves the current profile to the json file
        """
        profile_list = sorted(list(self.profiles.keys()))
        idx = profile_list.index(self.last_run_profile)
        try:
            next_profile = profile_list[idx + 1]
        except IndexError:
            next_profile = profile_list[0]
        # run the new profile script with subprocess, and save the mouse status
        try:
            mp = MouseProfile(name=next_profile, attrs=self.profiles[next_profile])
            mp.run()
            self.last_run_profile = next_profile
            self.save_status()
        except Exception as e:
            print("An exception occurred:")
            print(e)

        return


def main():
    mouse = Mouse()
    return mouse


if __name__ == "__main__":
    main()
