#!/usr/bin/env python3
# mouse_profile.py - a Python class representing a ratbagctl profile for Logitech G mice

from pathlib import Path
import re
import subprocess

from utils import get_bash_stdout
from mouse import Mouse


class MouseProfile:
    """
    TODO
        Attrs:
            mouse (Mouse): Mouse class from mouse.py
            name (str): the name of the profile, ex. "Default" or "Hades"
            report_rate (int): polling rate, in Hz
            resolutions (list(int)): list of DPI resolutions to set
            default_resolution (int): index of the default DPI
            buttons (list(str)): list of all the buttons and macros
            leds (list(dict)): list of dicts containing led properties
            sh_script (str): a big f-string that can be used to set the profile
    """

    def __init__(self, name="Default", mouse=Mouse()):
        self.mouse = mouse
        self.name = name
        # generate attrs using the current mouse settings
        report_rate = int(get_bash_stdout(f"ratbagctl {self.mouse.alias} rate get"))
        # iterate over all the set resolutions and get them into a list
        resolutions = []
        res_idx = 0
        res_re = re.compile(r"\d:\s(\d{,5})dpi.*")
        while True:
            res_out = get_bash_stdout(
                f"ratbagctl {self.mouse.alias} resolution {res_idx} get"
            )
            res_mo = res_re.match(res_out)
            if res_mo:
                resolutions.append(res_mo.group(1))
                res_idx += 1
            else:
                break

        # ratbagctl uses the resolution index for the default dpi
        #   so 'default_resolution' here is an index, not a dpi
        default_resolution = int(
            get_bash_stdout(f"ratbagctl {self.mouse.alias} resolution default get")
        )
        default_dpi = resolutions[default_resolution]

        # iterate over all the set buttons and get them into a list
        #   use .replace() to get 'command-ified' keypresses
        #       NOTE that macro waits are written like 't300' (wait 300ms)
        buttons = []
        btn_re = re.compile(r".*'(.*)'.*")
        for i in range(self.mouse.button_count):
            btn_out = get_bash_stdout(
                f"ratbagctl {self.mouse.alias} button {i} get"
            ).strip()
            btn_mo = btn_re.match(btn_out)
            buttons.append(
                btn_mo.group(1)
                .replace("↕", "KEY_")
                .replace("↓", "+KEY_")
                .replace("↑", "-KEY_")
            )

        # iterate over all the set LEDs and get them into a list of dicts
        #   we will later iterate over each dict and only set k-v pairs that exist
        leds = []
        led_idx = 0
        led_re = re.compile(
            r"LED: (\d), depth: rgb, mode: (on|off|cycle|breathing), color: (\w{6})|, duration: (\d{,5}), brightness: (\d{,3})"
        )
        while True:
            led_out = get_bash_stdout(f"ratbagctl {self.mouse.alias} led {led_idx} get")
            led_mo = led_re.match(led_out)
            if led_mo:
                leds.append(
                    {
                        "mode": led_mo.group(2),
                        "color": led_mo.group(3),
                        "duration": led_mo.group(4),
                        "brightness": led_mo.group(5),
                    }
                )
                led_idx += 1
            else:
                break

        ### GENERATE THE SHELL SCRIPT ###
        # all the symbols here can throw errors so we'll use a raw string
        raw_device_print = r" '{print $2}' | awk '{$1=$1};1')"

        # join up all the lines of the different sections
        res_lines = []
        for idx, dpi in enumerate(resolutions):
            res_lines.append(
                f'ratbagctl "$device" resolution {idx} dpi set {dpi} --nocommit'
            )
        joined_res_lines = "\n".join(res_lines)

        led_lines = []
        for idx, led in enumerate(leds):
            led_line = f'ratbagctl "$device" led {idx} set'
            for key, value in led.items():
                # we only want to set LED properties that exist
                if value:
                    led_line += f" {key} {value}"
            led_line += " --nocommit"
            led_lines.append(led_line)
        joined_led_lines = "\n".join(led_lines)

        btn_lines = []
        for idx, btn in enumerate(buttons):
            btn_line = f'ratbagctl "$device" button {idx} action set '
            if btn.startswith("button") is False:
                btn_line += f"macro "
            btn_line += btn
            # --nocommit waits to write all the properties to the mouse
            #   so the last line should NOT have '--nocommit'
            if not btn == buttons[-1]:
                btn_line += " --nocommit"
            btn_lines.append(btn_line)
        joined_btn_lines = "\n".join(btn_lines)

        sh_script = f"""#!/bin/bash
# {name}.sh - {name} mouse profile for Logitech {self.mouse.model.upper()}

profile_name="{name}"

device=$(ratbagctl list | grep -E 'G403' | awk -F: {raw_device_print}

ratbagctl "$device" profile active set 0 --nocommit

ratbagctl "$device" rate set {report_rate} --nocommit

{joined_res_lines}

ratbagctl "$device" resolution default set {default_resolution} --nocommit
ratbagctl "$device" dpi set {default_dpi} --nocommit

{joined_led_lines}

{joined_btn_lines}

echo "$profile_name profile set for $device"
"""
        # setting all the init attrs here at the end for ease of reading
        self.report_rate = report_rate
        self.resolutions = resolutions
        self.default_resolution = default_resolution
        self.buttons = buttons
        self.leds = leds
        self.sh_script = sh_script
        return

    def write_sh_to_file(self):
        sh_script_path = Path(self.mouse.folder / f"{self.name.lower()}.sh")
        with open(sh_script_path, "w") as fo:
            fo.write(self.sh_script)
        # give the script execute permissions
        subprocess.run(["chmod", "a+x", sh_script_path])
        return


def main():
    default_profile = MouseProfile()
    default_profile.write_sh_to_file()
    return


if __name__ == "__main__":
    main()
