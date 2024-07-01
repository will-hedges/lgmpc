#!/usr/bin/env python3

import re
import requests
import subprocess
import tempfile

from bs4 import BeautifulSoup

from utils import get_bash_stdout, get_mouse_alias_and_model


def color_hex_to_desc(color_hex):
    res = requests.get(f"https://www.colorhexa.com/{color_hex}")
    res.raise_for_status()
    soup = BeautifulSoup(res.text, features="html.parser")
    color = soup.select(".color-description p strong").pop().get_text()
    return color.lower()


class MouseProfile:
    """
    TODO
        Attrs:
            name (str): the name of the profile, ex. "Default" or "Hades"
            report_rate (int): polling rate, in Hz
            resolutions (list(int)): list of DPI resolutions to set
            default_resolution (int): index of the default DPI
            buttons (list(str)): list of all the buttons and macros
            leds (list(dict)): list of dicts containing led properties
    """

    def __init__(self, name="default", attrs={}):
        # if the user doesn't pass the attrs dict, get all of it from ratbagctl
        if attrs == {}:
            self.name = name
            # NOTE don't set device as an attr because we don't want it in MouseProfile.__dict__
            device = get_mouse_alias_and_model()[0]
            # generate attrs using the current mouse settings
            # TODO get the mouse button count
            btn_ct = int(get_bash_stdout(f"ratbagctl {device} button count"))

            # start with polling rate
            self.report_rate = int(get_bash_stdout(f"ratbagctl {device} rate get"))

            # iterate over all the set resolutions and get them into a list
            self.resolutions = []
            res_idx = 0
            res_re = re.compile(r"\d:\s(\d{,5})dpi.*")
            while True:
                res_out = get_bash_stdout(
                    f"ratbagctl {device} resolution {res_idx} get"
                )
                res_mo = res_re.match(res_out)
                if res_mo:
                    self.resolutions.append(int(res_mo.group(1)))
                    res_idx += 1
                else:
                    break

            # ratbagctl uses the resolution index for the default dpi
            #   so 'default_resolution' here is an index, not a dpi
            self.default_resolution = int(
                get_bash_stdout(f"ratbagctl {device} resolution default get")
            )

            # iterate over all the set buttons and get them into a list
            #   use .replace() to get 'command-ified' keypresses
            #       NOTE macro waits are written like 't300' (wait 300ms)
            self.buttons = []
            btn_re = re.compile(r".*'(.*)'.*")
            for i in range(btn_ct):
                btn_out = get_bash_stdout(f"ratbagctl {device} button {i} get").strip()
                btn_mo = btn_re.match(btn_out)
                self.buttons.append(
                    btn_mo.group(1)
                    .replace("↕", "KEY_")
                    .replace("↓", "+KEY_")
                    .replace("↑", "-KEY_")
                )

            # iterate over all the set LEDs and get them into a list of dicts
            #   we will later iterate over each dict and only set k-v pairs that exist
            self.leds = []
            led_idx = 0
            led_re = re.compile(
                r"LED: (\d), depth: rgb, mode: (on|off|cycle|breathing), color: (\w{6})|, duration: (\d{,5}), brightness: (\d{,3})"
            )
            while True:
                led_out = get_bash_stdout(f"ratbagctl {device} led {led_idx} get")
                led_mo = led_re.match(led_out)
                if led_mo:
                    mode, color, duration, brightness = led_mo.groups()[1:]
                    # brightness will not always display out from ratbagctl
                    # if this happens, just set max (255)
                    if brightness is None:
                        brightness = 255
                    self.leds.append(
                        {
                            "mode": mode,
                            "color": color,
                            "duration": duration,
                            "brightness": brightness,
                        }
                    )
                    led_idx += 1
                else:
                    break
        else:
            self.name = attrs["name"]
            self.report_rate = attrs["report_rate"]
            self.resolutions = attrs["resolutions"]
            self.default_resolution = attrs["default_resolution"]
            self.buttons = attrs["buttons"]
            self.leds = attrs["leds"]

        return

    def run(self):
        device, model = get_mouse_alias_and_model()

        commands = []
        # set the polling rate
        commands.append(f"\nratbagctl --nocommit {device} rate set {self.report_rate}")
        # set the resolutions
        for idx, dpi in enumerate(self.resolutions):
            commands.append(
                f"\nratbagctl --nocommit {device} resolution {idx} dpi set {dpi}"
            )
        # set default resolution and dpi
        commands.append(
            f"\nratbagctl --nocommit {device} resolution default set {self.default_resolution}"
        )
        commands.append(
            f"\nratbagctl --nocommit {device} dpi set {self.resolutions[self.default_resolution]}"
        )

        # set the buttons
        for idx, btn in enumerate(self.buttons):
            cmd = f"\nratbagctl --nocommit {device} button {idx} action set"
            if btn.startswith(("-", "+", "KEY", "t")):
                cmd += " macro "
            cmd += " " + btn
            commands.append(cmd)

        # set the LEDs
        for idx, led in enumerate(self.leds):
            cmd = f"\nratbagctl --nocommit {device} led {idx} set"
            for key, value in led.items():
                if value:
                    cmd += f" {key} {value}"
            commands.append(cmd)

        # remove '--nocommit' from the last line
        #   this will send the whole profile at once
        last_command = commands.pop()
        last_command = last_command.replace(" --nocommit ", " ")
        commands.append(last_command)
        with tempfile.NamedTemporaryFile() as tmp:
            tmp_sh = tmp.name + ".sh"
            with open(tmp_sh, "w") as sh_file:
                sh_file.writelines(commands)
            try:
                subprocess.run(["sh", tmp_sh])
                print(f"Profile '{self.name}' successfully written to {model.upper()}")
            except Exception as e:
                print(f"An Exception occurred: {e}")

        return

    def show(self):
        print(f"Profile: {self.name}")
        print(f"  Polling rate: {self.report_rate} Hz")
        print(f"  Resolutions:")
        for idx, res in enumerate(self.resolutions):
            # hide inactive resolutions
            if res != 0:
                res_str = f"{idx}: {res} dpi"
                if idx == self.default_resolution:
                    res_str += " (default)"
            if res > 0:
                print("    " + res_str)
        print(f"  Buttons:")
        for idx, btn in enumerate(self.buttons):
            btn_str = f"    button {idx}: "
            if btn.startswith("button"):
                btn_str += f"{btn}"
            elif btn.startswith(("KEY_", "+", "-", "t")):
                btn_str += f"macro {btn}"
            print(btn_str)
        print("  LEDs:")
        for idx, led in enumerate(self.leds):
            print(f"    led {idx}:")
            for prop, val in led.items():
                if val:
                    led_str = f"      {prop}: {val}"
                    if prop == "color":
                        color_name = color_hex_to_desc(val)
                        led_str += f" '{color_name}'"
                    if prop == "brightness" and val == 255:
                        led_str += " (max)"
                    print(led_str)
