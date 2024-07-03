# Logitech G Mouse Profile Manager (lgmpm)
A simple command-line tool for managing profiles for Logitech G mice on Linux

## Introduction
As more gamers move to Linux, `ratbagctl` and [Piper](https://github.com/libratbag/piper) are great FOSS replacements for Logitech Gaming Software, etc. 
However, LGS manages profiles very well at the software level while [storing and loading profiles with Piper is not supported.](https://github.com/libratbag/piper/issues/631)

This pure Python project aims to replace some of the missing profiling capabilities.

## Setup

1. Clone this repo to your desired directory with `git clone` and move into the directory
   
    ```
    $ git clone https://github.com/will-hedges/lgmpm
    $ cd lgmpm/
    ```

2. Install dependencies in `requirements.txt`
    
    ```
    $ pip install -r requirements.txt
    ```

3. Run the program - this will automatically set up a `default` profile with the current mouse settings

    ```
    $ python3 lgmpm.py
    ```
    **NOTE:** this project is only designed to target one mouse and currently does not support multiple mice connected at the same time. However, different mouse models will have their profile data stored in separate files.
    
For a list of available commands, run the program with the `--help` or `-h` flag

    ```
    $ python3 lgmpm.py --help
    usage: lgmpm.py [-h] [-a] [-c] [-d] [-l] [-n] [-s] [-u] [profile_name]

    manages profiles for Logitech G mice using ratbagctl

    positional arguments:
      profile_name  the name of the profile
    
    options:
      -h, --help    show this help message and exit
      -a, --active  make <profile_name> the active profile
      -c, --cycle   cycle (up) to the next stored profile, if one exists
      -d, --delete  delete <profile_name>
      -l, --list    list all saved profiles for the connected mouse
      -n, --new     create a new profile with called <profile_name>
      -s, --show    show the saved settings for <profile_name>
      -u, --update  update <profile_name> with the current mouse settings

    ```

### Additional Setup (Optional)
There are multiple ways to make this program more convenient to use:

1. add the project dir to `$PATH` (then run the program from anywhere)
    
    i. open `~/.bashrc` with your favorite text editor

        $ nano ~/.bashrc
    
    ii. add the following to the bottom:
    
        export PATH=/path/to/project/directory:$PATH
    
    iii. save the modified file and reload it with `source`
        
        $ source ~/.bashrc
    
    iv. run the program with `python3 lgmpm.py -a default` etc.
    
2. create an `alias` in `~/.bashrc` (then run the program from anywhere)

    i. open `~/.bashrc` with your favorite text editor
    
    ii. add the following to the bottom:
        
        alias lgmpm='python3 /path/to/project/directory/lgmpmp.py'
    
    iii. save the modified file and reload it with `source`
        
        $ source ~/.bashrc
    
    iv. run the program with `lgmpm -a default` etc.
    
3. assign the `--cycle` function in KDE Shortcuts (or similar)
    
    ![](https://i.imgur.com/TuIGxMc.png)

    **NOTE:** you can even bind this shortcut to your mouse and cycle profiles from a button click
    

## Contributing

I code for fun and enjoy using my own projects. If you come across an issue, have a suggestion, or want to submit your own enhancement, please don't hesitate to reach out by [opening an issue](https://github.com/will-hedges/lgmpm/issues/), or [opening a pull request](https://github.com/will-hedges/lgmpm/pulls).
