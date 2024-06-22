#!/usr/bin/env python3

import re
import subprocess
import tempfile

from utils import get_bash_stdout, get_mouse_alias_and_model


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

    def __init__(self, name="default"):
        # NOTE don't set device as an attr because we don't want it in MouseProfile.__dict__
        device = get_mouse_alias_and_model()[0]
        # generate attrs using the current mouse settings
        # TODO get the mouse button count
        btn_ct = int(get_bash_stdout(f"ratbagctl {device} button count"))

        # start with polling rate
        report_rate = int(get_bash_stdout(f"ratbagctl {device} rate get"))

        # iterate over all the set resolutions and get them into a list
        resolutions = []
        res_idx = 0
        res_re = re.compile(r"\d:\s(\d{,5})dpi.*")
        while True:
            res_out = get_bash_stdout(f"ratbagctl {device} resolution {res_idx} get")
            res_mo = res_re.match(res_out)
            if res_mo:
                resolutions.append(res_mo.group(1))
                res_idx += 1
            else:
                break

        # ratbagctl uses the resolution index for the default dpi
        #   so 'default_resolution' here is an index, not a dpi
        default_resolution = int(
            get_bash_stdout(f"ratbagctl {device} resolution default get")
        )

        # iterate over all the set buttons and get them into a list
        #   use .replace() to get 'command-ified' keypresses
        #       NOTE macro waits are written like 't300' (wait 300ms)
        buttons = []
        btn_re = re.compile(r".*'(.*)'.*")
        for i in range(btn_ct):
            btn_out = get_bash_stdout(f"ratbagctl {device} button {i} get").strip()
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
            led_out = get_bash_stdout(f"ratbagctl {device} led {led_idx} get")
            led_mo = led_re.match(led_out)
            if led_mo:
                mode, color, duration, brightness = led_mo.groups()[1:]
                # brightness will not always display out from ratbagctl
                # if this happens, just set max (255)
                if brightness is None:
                    brightness = 255
                leds.append(
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

        # setting all the init attrs here at the end for ease of reading
        self.name = name
        self.report_rate = report_rate
        self.resolutions = resolutions
        self.default_resolution = default_resolution
        self.buttons = buttons
        self.leds = leds
        return

    def run(self):
        device = get_mouse_alias_and_model()[0]

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
                print("success")
            subprocess.run(["sh", tmp_sh])

        return


def main():
    mp = MouseProfile()
    mp.run()
    return


if __name__ == "__main__":
    main()
