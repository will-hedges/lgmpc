#!/usr/bin/env python3
# mouse_profile.py - a Python class representing a ratbagctl profile for Logitech G mice

from pathlib import Path
import re
import subprocess

import lgmp
from mouse import Mouse


class MouseProfile:
    """
    TODO
        Attrs:
            report_rate (int): TODO
            resolutions (list(int)): TODO
            buttons (list(str)): TODO
    """

    def __init__(self, name, mouse):
        self.mouse = mouse
        self.name = name
        # generate attrs using the current mouse settings
        report_rate = int(
            lgmp.get_bash_stdout(f"ratbagctl {self.mouse.alias} rate get")
        )

        resolutions = []
        res_idx = 0
        res_re = re.compile(r"\d:\s(\d{,5})dpi.*")
        while True:
            res_out = lgmp.get_bash_stdout(
                f"ratbagctl {self.mouse.alias} resolution {res_idx} get"
            )
            res_mo = res_re.match(res_out)
            if res_mo:
                resolutions.append(res_mo.group(1))
                res_idx += 1
            else:
                break

        # ratbagctl uses the resolution index for the default dpi
        # so 'default_resolution' here is an index, not a dpi
        default_resolution = int(
            lgmp.get_bash_stdout(f"ratbagctl {self.mouse.alias} resolution default get")
        )
        default_dpi = resolutions[default_resolution]

        buttons = []
        btn_re = re.compile(r".*'(.*)'.*")
        for i in range(self.mouse.button_count):
            btn_out = lgmp.get_bash_stdout(
                f"ratbagctl {self.mouse.alias} button {i} get"
            ).strip()
            btn_mo = btn_re.match(btn_out)
            buttons.append(
                btn_mo.group(1)
                .replace("↕", "KEY_")
                .replace("↓", "+KEY_")
                .replace("↑", "-KEY_")
            )

        leds = []
        led_idx = 0
        led_re = re.compile(
            r"LED: (\d), depth: rgb, mode: (on|off|cycle|breathing), color: (\w{6})|, duration: (\d{,5}), brightness: (\d{,3})"
        )
        while True:
            led_out = lgmp.get_bash_stdout(
                f"ratbagctl {self.mouse.alias} led {led_idx} get"
            )
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

        # generate the .sh script
        raw_device_print = r" '{print $2}' | awk '{$1=$1};1')"

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
            if not btn == buttons[-1]:
                btn_line += " --nocommit"
            btn_lines.append(btn_line)
        joined_btn_lines = "\n".join(btn_lines)

        sh_script = f"""#!/bin/bash
# {name}.sh - {name} mouse profile for Logitech {self.mouse.model}

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

        self.report_rate = report_rate
        self.resolutions = resolutions
        self.default_resolution = default_resolution
        self.buttons = buttons
        self.leds = leds
        self.sh_script = sh_script
        return

    def write_to_sh_script(self):
        sh_script_path = Path(self.mouse.folder / f"{self.name}.sh")
        with open(sh_script_path, "w") as fo:
            fo.write(self.sh_script)
        # give the script execute permissions
        subprocess.run(["chmod", "a+x", sh_script_path])
        return


def main():
    mouseProfile = MouseProfile("Default", Mouse())
    mouseProfile.write_to_sh_script()
    return


if __name__ == "__main__":
    main()
