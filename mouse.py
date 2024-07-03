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

        Attributes:
            alias (str): the ratbagctl 'short name' of the mouse, ex. 'dancing-puppy'
            model (str): a short version of the mouse model, ex. 'g403'
            model_json  (Path): a Path object that to the json file for a particular mouse model
            last_active_profile (str): the name of the last profile that was run from this program
            profiles (dict): a nested dict containing the data for each profile
    """

    def __init__(self):
        """
        Loads the mouse model's profile data, or creates default if none exists
        """
        alias, model = get_mouse_alias_and_model()
        model_json_fp = Path(__file__).parent / "models" / f"{model}.json"
        try:
            with open(model_json_fp, "r") as jf:
                mouse_data = json.load(jf)

        except (FileNotFoundError, json.decoder.JSONDecodeError):

            model_json_fp.touch()
            mp = MouseProfile()
            mouse_data = {}
            # since 'default' is the only profile that exists, set it as last active
            last_active_profile = mp.name
            mouse_data["last_active_profile"] = last_active_profile
            # initialize a dict of profiles with 'default' being the only key
            mouse_data["profiles"] = {}
            mouse_data["profiles"][mp.name] = mp.__dict__

            with open(model_json_fp, "w") as jf:
                json.dump(mouse_data, jf, indent=2)

        self.alias = alias
        self.model = model
        self.model_json = model_json_fp
        # TODO need some handling for if the last active profile doesnt exist
        # TODO or if self.profiles is now blank
        self.last_active_profile = mouse_data["last_active_profile"]
        self.profiles = mouse_data["profiles"]
        return

    def save_status(self):
        """
        Saves the last active profile & other profiles to {model}.json
        """
        mouse_data = {
            "last_active_profile": self.last_active_profile,
            "profiles": self.profiles,
        }
        with open(self.model_json, "w") as jf:
            json.dump(mouse_data, jf, indent=2)
        return

    def set_active_profile(self, profile_name):
        """
        Loads/writes the selected profile onto the mouse and updates the last active profile
            Parameters:
                profile_name (str): the name of the profile to set active
        """
        try:
            mp = MouseProfile(
                name=profile_name,
                attrs=self.profiles[profile_name],
            )
            mp.run()
            self.save_status()
        except KeyError:
            print(f"No stored {self.model.upper()} profile '{profile_name}'")
            print_list_msg()
            print_help_msg()
        return

    def cycle_profile(self):
        """
        Cycles through and runs the next profile from last active, sorted alphabetically
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
            idx = profile_list.index(self.last_active_profile)
            try:
                next_profile = profile_list[idx + 1]
            except IndexError:
                next_profile = profile_list[0]
            # run the new profile script with subprocess
            #   and save the mouse status
            try:
                mp = MouseProfile(
                    name=next_profile,
                    attrs=self.profiles[next_profile],
                )
                mp.run()
                self.last_active_profile = next_profile
                self.save_status()
            except Exception as e:
                print("An exception occurred:")
                print(e)
        return

    def delete_profile(self, profile_name):
        """
        Deletes a profile from {model}.json
            Parameters:
                profile_name (str): the name of the profile to delete
        """
        try:
            del self.profiles[profile_name]
            if self.last_active_profile == profile_name:
                self.last_active_profile = "default"
            self.save_status()
            # TODO need some handling here for if there is no default profile
            # TODO or if the user deletes the only profile
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
            Parameters:
                profile_name (str): the name of the new profile to save
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
            self.last_active_profile = profile_name
            self.save_status()
        return

    def show_profile(self, profile_name):
        """
        Displays the profile data similar to running 'ratbagctl {alias} info'
            Parameters:
                profile_name (str): the name of the profile to show
        """
        # get the 'long form' name of the mouse for display
        #   i.e. 'Logitech G403 Prodigy Gaming Mouse' instead of 'g403'
        full_mouse_name = get_bash_stdout(f"ratbagctl {self.alias} name").strip()
        profile_attrs = self.profiles[profile_name]
        mp = MouseProfile(name=profile_name, attrs=profile_attrs)
        print(f"{full_mouse_name} aka '{self.alias}'")
        mp.show()
        return

    def update_profile(self, profile_name):
        """
        Updates an existing saved profile with the current mouse settings
            Parameters:
                profile_name (str): the name of the profile to update
        """
        try:
            updated_profile = MouseProfile(name=profile_name)
            self.profiles[profile_name].update(updated_profile.__dict__)
            self.last_active_profile = profile_name
            self.save_status()
        except KeyError:
            print(f"Could not find {self.model.upper()} profile '{profile_name}'")
            print_list_msg()
            print_help_msg()
        return
