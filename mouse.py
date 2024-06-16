#!/usr/bin/env python3
# mouse.py - a Python class representing a Logitech G mouse

from pathlib import Path
import pickle
import re
import subprocess

from utils import get_bash_stdout


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
def get_pickled_profile(fp):
    """
    Pulls in the path of the last set profile from the pickle file
        or creates a pickle file if it does not already exist

        Params:
            fp (Path): the Path of the mouse model directory
        Returns:
            current_profile (Path): the full path of the last pickled profile .sh
    """

    pickle_path = Path(fp / f"{fp.name}.pickle")
    try:
        with open(pickle_path, "rb") as pf:
            current_profile = pickle.load(pf)
    except (FileNotFoundError, EOFError):
        pickle_path.touch()
        current_profile = Path(fp / "default.sh")
        current_profile.touch()
        # TODO should make the default.sh here

    return current_profile


def save_pickled_profile(pickle_fp, profile_fp):
    """
    Saves the path of the currently set profile .sh to pickle file
        Params:
            pickle_fp (Path): the Path to the pickle file
            profile_fp (Path): the Path to the profile shell script
    """
    with open(pickle_fp, "wb") as pf:
        pickle.dump(profile_fp, pf)
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
        self.alias, self.model = get_mouse_alias_and_model()
        self.button_count = get_button_count(self.alias)
        self.folder = Path(__file__).parent / "models" / self.model
        # if the model's folder doesn't exist, create it
        self.folder.mkdir(parents=True, exist_ok=True)
        self.profiles = get_all_shell_scripts_in(self.folder)
        return

    def cycle_profile(self):
        """
        Cycles through and runs the "next" indexed profile shell script
            then saves the current profile to the pickle file
        """
        current_profile = get_pickled_profile(self.folder)
        current_idx = self.profiles.index(current_profile)
        try:
            current_profile = self.profiles[current_idx + 1]
        except IndexError:
            current_profile = self.profiles[0]
        self.current_profile = current_profile
        # run the new profile script with subprocess
        subprocess.run(["sh", current_profile])
        # write out the new profile to pickle
        pickle_fp = Path(self.folder / f"{self.model}.pickle")
        save_pickled_profile(pickle_fp, current_profile)
        return
