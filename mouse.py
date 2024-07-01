#!/usr/bin/env python3
# mouse.py - a Python class representing a Logitech G mouse

import json
from pathlib import Path

from mouseprofile import MouseProfile
from utils import (
    get_bash_stdout,
    print_help_msg,
    print_list_msg,
    get_mouse_alias_and_model,
)


class Mouse:
    """
    A class to represent a Logitech G mouse
        TODO docstring
    """

    def __init__(self):
        # try to load from json
        # if no {model}.json, we will make one and set 'profiles' and
        #   'last_run_profile' keys
        alias, model = get_mouse_alias_and_model()
        model_json_fp = Path(__file__).parent / "models" / f"{model}.json"
        try:
            with open(model_json_fp, "r") as jf:
                mouse_data = json.load(jf)
        # catch if the file doesn't exist yet, or is blank
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            # create the file, the 'default' profile, and a dict representing
            #   both the mouse and its profiles
            model_json_fp.touch()
            mp = MouseProfile()
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
        """
        Saves the mouse, profile data to {model.json}
        """
        mouse_data = {
            "last_run_profile": self.last_run_profile,
            "profiles": self.profiles,
        }
        with open(self.model_json, "w") as jf:
            json.dump(mouse_data, jf, indent=2)
        return

    def set_active_profile(self, profile_name):
        """
        Loads/writes the selected profile onto the mouse
        """
        try:
            mp = MouseProfile(
                name=profile_name,
                attrs=self.profiles[profile_name],
            )
            mp.run()
            # set the last active profile
            self.save_status()
        except KeyError:
            print(f"No stored {self.model.upper()} profile '{profile_name}'")
            print_list_msg()
            print_help_msg()
        return

    def cycle_profile(self):
        """
        Cycles through and runs the "next" indexed profile shell script
            then saves the current profile to the json file
        """
        # check to see if there is only one profile saved, since there should
        #   always be at least one profile, or default, even if there was no
        #       json file prior to first time setup
        # NOTE the user could delete the default profile, so we will just show
        #   whatever profile name is there
        if len(self.profiles) == 1:
            sole_profile_name = tuple(self.profiles.keys())[0]
            print(f"Only 1 profile found: '{sole_profile_name}'")
            print_help_msg()

        else:
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

    def delete_profile(self, profile_name):
        """
        Deletes a profile from {model}.json
        """
        try:
            del self.profiles[profile_name]
            # if the user deleted the last run profile
            #   set last run profile to 'default' and save to file
            if self.last_run_profile == profile_name:
                self.last_run_profile = "default"
            self.save_status()
        except KeyError:
            print(f"The profile {profile_name} does not exist for this mouse.")
            print_list_msg()
            print_help_msg()
        return

    def list_profiles(self):
        """
        Lists all the saved profiles in {model}.json
        """
        print(f"Found the following {self.model.upper()} profiles:")
        for idx, name in enumerate(sorted(self.profiles)):
            print(f"  {idx + 1}. {name}")
        print_help_msg()
        return

    def add_new_profile(self, profile_name):
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
            new_profile = MouseProfile(name=profile_name)
            self.profiles[profile_name] = new_profile.__dict__
            self.last_run_profile = profile_name
            self.save_status()
        return

    def show_profile(self, profile_name):
        """
        Displays the profile data in a format similar to the output of
            'ratbagctl {alias} info'
        """
        # get the 'long form' name of the mouse for display
        #   i.e. 'Logitech G403 Prodigy Gaming Mouse' instead of 'g403'
        full_mouse_name = get_bash_stdout(f"ratbagctl {self.alias} name").strip()
        profile_attrs = self.profiles[profile_name]
        mp = MouseProfile(name=profile_name, attrs=profile_attrs)
        print(f"{full_mouse_name} aka '{self.alias}'")
        mp.show()
        return

    def update_profile(self, profile_name, profile_dict):
        """
        Updates an existing saved profile with the current mouse settings,
            updates the last run profile, and saves the current status to {model}.json
        """
        try:
            updated_profile = MouseProfile(name=profile_name)
            self.profiles[profile_name].update(updated_profile.__dict__)
            self.last_run_profile = profile_name
            self.save_status()
        except KeyError:
            print(f"Could not find {self.model.upper()} profile '{profile_name}'")
            print_list_msg()
            print_help_msg()
        return
