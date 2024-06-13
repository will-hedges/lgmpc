#!/usr/bin/env python3
# mouse.py - a Python class representing a Logitech G mouse

from pathlib import Path
import re

import lgmp
from mouse_profile import MouseProfile


class Mouse:
    """
    A class to represent a Logitech G mouse

        Attrs:
            alias (str): the ratbagctl short name of the mouse
            model (str): the Logitech model name/number of the mouse
            button_count (int): the number of buttons the mouse has
            folder (Path): the directory containing profiles and pickle files for the mouse
            profiles (list): a list of Path objects of all the local mouse profiles

        Methods:
            get_all_profiles TODO
            read_active_profile TODO
            load_pickle TODO
            save_pickle TODO
    """

    def __init__(self):
        self.alias, self.model = lgmp.get_mouse_alias_and_model()
        self.button_count = lgmp.get_button_count(self.alias)
        self.folder = Path(__file__).parent / "models" / self.model
        # if the model's folder doesn't exist, make it
        self.folder.mkdir(parents=True, exist_ok=True)
        return

    def get_all_profiles(self):
        """
        Creates a list of all the the .sh profile scripts within self.folder
            and assigns them to self.profiles
        """
        profile_glob = sorted(self.folder.glob("*.sh"))
        # TODO if no profiles, create one with the current mouse settings
        #   and save it to default.sh
        profiles = [Path(profile) for profile in profile_glob]
        self.profiles = profiles
        return

    def read_active_profile(self):
        """
        Creates a dictionary from the current mouse settings

            Returns:
                mouse_profile (dict) TODO
        """
        report_rate = int(lgmp.get_bash_stdout(f"ratbagctl {self.alias} rate get"))

        resolutions = []
        r = 0
        res_re = re.compile(r"\d:\s(\d{,5})dpi.*")
        while True:
            res_out = lgmp.get_bash_stdout(f"ratbagctl {self.alias} resolution {r} get")
            res_mo = res_re.match(res_out)
            if res_mo:
                resolutions.append(res_mo.group(1))
                r += 1
            else:
                break

        buttons = []
        btn_re = re.compile(r".*'(.*)'.*")
        for i in range(self.button_count):
            btn_out = lgmp.get_bash_stdout(
                f"ratbagctl {self.alias} button {i} get"
            ).strip()
            btn_mo = btn_re.match(btn_out)
            buttons.append(
                btn_mo.group(1)
                .replace("↕", "KEY_")
                .replace("↓", "+KEY_")
                .replace("↑", "-KEY_")
            )

        leds = []
        l = 0
        led_re = re.compile(
            r"LED: (\d), depth: rgb, mode: (on|off|cycle|breathing), color: (\w{6})|, duration: (\d{,5}), brightness: (\d{,3})"
        )
        while True:
            led_out = lgmp.get_bash_stdout(f"ratbagctl {self.alias} led {l} get")
            led_mo = led_re.match(led_out)
            if led_mo:
                leds.append(led_mo.groups())
                l += 1
            else:
                break

        mouse_profile = {
            "report_rate": report_rate,
            "resolutions": resolutions,
            "buttons": buttons,
            "leds": leds,
        }

        return mouse_profile

    def load_pickle(self):
        return

    def save_pickle(self):
        return

    def cycle_profile(self):
        return


def main():
    mouse = Mouse()
    mouse.read_active_profile()
    return


if __name__ == "__main__":
    main()
