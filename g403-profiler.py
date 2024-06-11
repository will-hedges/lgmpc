#!/usr/bin/env python3
# g403-profiler.py - script to cycle Logitech mouse profiles


from pathlib import Path
import pickle
import re
import subprocess


def get_mouse_alias_and_model():
    ratbagctl_list_out = subprocess.run(
        ["ratbagctl", "list"], stdout=subprocess.PIPE
    ).stdout.decode()

    mouse_re = re.compile(r"([a-z-]+):\s+Logitech\s(\w+).*")
    mouse_mo = mouse_re.match(ratbagctl_list_out)

    alias = mouse_mo.group(1)
    model = mouse_mo.group(2).lower()

    return (alias, model)


class Mouse:

    def __init__(self):
        self.alias, self.model = get_mouse_alias_and_model()
        self.profile_dir = Path(__file__).parent / f"{self.model}-profiles"
        self.pickle_file = Path(self.profile_dir / f"{self.model}-pickle")
        return

    def get_all_profiles(self):
        profile_glob = sorted(self.profile_dir.glob("*.sh"))
        profiles = [Path.absolute(Path(profile)) for profile in profile_glob]
        self.profiles = profiles
        return

    def load_profile_from_pickle(self):
        try:
            with open(self.pickle_file, "rb") as pf:
                current_profile = pickle.load(pf)
        except FileNotFoundError:
            current_profile = self.profile_dir / f"{self.model}-default.sh"
            with open(self.pickle_file, "wb") as pf:
                pickle.dump(current_profile, pf)

        self.current_profile = current_profile
        self.profile_index = self.profiles.index(current_profile)
        return

    def cycle_profile(self):
        try:
            self.profile_index += 1
            self.current_profile = self.profiles[self.profile_index]
        except IndexError:
            self.profile_index = 0
            self.current_profile = self.profiles[self.profile_index]

        subprocess.run(self.current_profile)
        return

    def dump_profile_to_pickle(self):
        with open(self.pickle_file, "wb") as pf:
            pickle.dump(self.current_profile, pf)
        return


def main():
    mouse = Mouse()
    mouse.get_all_profiles()
    mouse.load_profile_from_pickle()
    mouse.cycle_profile()
    mouse.dump_profile_to_pickle()
    return


if __name__ == "__main__":
    main()
