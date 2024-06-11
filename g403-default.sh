#!/bin/bash
# g403-default.sh - default mouse profile for my G403

profile_name="Default"

# Set the device name
device=$(ratbagctl list | grep -E 'Logitech G403 Prodigy Gaming Mouse' | awk -F: '{print $2}' | awk '{$1=$1};1')

# Set the profile (0 is default)
ratbagctl "$device" profile active set 0 --nocommit

# Set the DPI
ratbagctl "$device" dpi set 1600 --nocommit

# Set the polling rate
# ratbagctl "$device" rate set 1000 --nocommit

# Set the LED colors
ratbagctl "$device" led 0 set mode on color 9141ac --nocommit
ratbagctl "$device" led 1 set mode on color 9141ac --nocommit

# Reset the button mappings
# ratbagctl "$device" button 0 action set button 1 --nocommit   # left click
# ratbagctl "$device" button 1 action set button 2 --nocommit   # right click
# ratbagctl "$device" button 2 action set button 3 --nocommit   # middle click
ratbagctl "$device" button 3 action set macro +KEY_LEFTCTRL KEY_C -KEY_LEFTCTRL --nocommit  # back button
ratbagctl "$device" button 4 action set macro +KEY_LEFTCTRL KEY_V -KEY_LEFTCTRL --nocommit  # forward button
ratbagctl "$device" button 5 action set macro +KEY_LEFTMETA KEY_M -KEY_LEFTMETA             # top button

echo "$profile_name profile set for $device"      
