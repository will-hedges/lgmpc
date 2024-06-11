#!/bin/bash
# hd2.sh - sets Helldivers 2 mouse profile for G403 mouse

profile_name="HD2"

# Set the device name
device=$(ratbagctl list | grep -E 'Logitech G403 Prodigy Gaming Mouse' | awk -F: '{print $2}' | awk '{$1=$1};1')

# Set the profile (0 is default)
ratbagctl "$device" profile active set 0 --nocommit

# Set the DPI
ratbagctl "$device" dpi set 800 --nocommit

# Set the polling rate
# ratbagctl "$device" rate set 1000 --nocommit

# Set the LED colors
ratbagctl "$device" led 0 set mode on color e5a50a --nocommit
ratbagctl "$device" led 1 set mode on color e5a50a --nocommit

# Reset the button mappings
# ratbagctl "$device" button 0 action set button 1 --nocommit   # left click
# ratbagctl "$device" button 1 action set button 2 --nocommit   # right click
# ratbagctl "$device" button 2 action set button 3 --nocommit   # middle click
ratbagctl "$device" button 3 action set button 4 --nocommit     # back button
ratbagctl "$device" button 4 action set button 5                # forward button
# ratbagctl "$device" button 5 action set button 6              # top button

echo "$profile_name profile set for $device"
