#!/usr/bin/env python3
# lgmpc.py - Logitech G Mouse Profile Cycler
#   a script to cycle Logitech G mouse profiles with ratbagctl


from mouse import Mouse


def main():
    mouse = Mouse()
    mouse.cycle_profile()
    return


if __name__ == "__main__":
    main()
