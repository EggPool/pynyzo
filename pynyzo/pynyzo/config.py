"""
PyNyzo
Common variables

Also serves as config file for POC and tests
"""

from os import path
from pynyzo.keyutil import KeyUtil
from pynyzo.byteutil import ByteUtil

__version__ = '0.0.1'

"""
User config - You can change these ones, but **See doc**
Please use config.txt instead of editing here.  

This file is only to be edited by dev or for debug purposes.
"""

VERBOSE = True

# Dev only - break nice color
DEBUG = False

# Dev only, dumps network packets
DUMP_PACKETS = False

# optional log details we may want. AVAILABLE_LOGS lists all possible extra details.
# Copy the ones you want in LOG
LOG = []

AVAILABLE_LOGS = ['keys', 'connections', 'timing']

# Path to the privkey
NYZO_SEED = "tmp/verifier_private_seed"

PYTHON_EXECUTABLE = "python3"


"""
Here comes tuneable algorithm variables - Do not change those or you may  be unable to sync
"""

# Default Nyzo port
DEFAULT_PORT = 9444

# How long to wait before retrying a failed peer?
PEER_RETRY_SECONDS = 20

# Seconds between pings
PING_DELAY = 30

"""
DEBUG VARS
"""

NETWORK_TIMEOUT = 300

"""
Global Variables
"""

PRIVATE_KEY = b''
PUBLIC_KEY = b''

# --------------------------------------------------- #

# The potential variables and their type
_VARS = {
    "VERBOSE": "bool",
    "DEBUG": "bool",
    "DUMP_PACKETS": "bool",
    "LOG": "list",
    "NYZO_SEED": "str",
    "PYTHON_EXECUTABLE": "str",
    "PEER_RETRY_SECONDS": "int",
    "PING_DELAY": "int",
    "NETWORK_TIMEOUT": "int"
}


def _get_left_right(line, var_list):
    left, right = map(str.strip, line.rstrip("\n").split("="))
    if left not in var_list:
        return None, None
    param = var_list[left]
    if param == "int":
        right = int(right)
    elif param == "float":
        right = float(right)
    elif param == "list":
        # Separator may be ; or ,
        right = [str(item.strip()) for item in right.replace(';', ',').split(",")]
    elif param == "bool":
        if right.lower() in ["false", "0", "", "no"]:
            right = False
        else:
            right = True
    else:
        # treat as "str"
        pass
    return left, right


def _overload(file_name: str):
    for line in open(file_name):
        if line and line[0] == '#':
            continue
        if '=' in line:
            left, right = _get_left_right(line, _VARS)
            if left:
                globals().update({left: right})


def load(dir: str='./'):
    """
    Overload info with config.default.txt and config.txt
    :return:
    """
    global PRIVATE_KEY
    global PUBLIC_KEY
    if path.exists(dir + "config.default.txt"):
        _overload(dir + "config.default.txt")
    if path.exists(dir + "config.txt"):
        _overload(dir + "config.txt")

    # Load the keys
    if not path.isfile(NYZO_SEED):
        print(f"No key file, creating one into {NYZO_SEED}")
        PRIVATE_KEY = KeyUtil.generateSeed()
        KeyUtil.save_to_private_seed_file(NYZO_SEED, PRIVATE_KEY)
    PRIVATE_KEY, PUBLIC_KEY = KeyUtil.get_from_private_seed_file(NYZO_SEED)
    # We can tweak verbosity later on, do not print here but later on.
    if DEBUG:
        print(f"Key Loaded, public id {ByteUtil.bytes_as_string_with_dashes(PUBLIC_KEY.to_bytes())}")

    return {var: globals()[var] for var in _VARS}


if __name__ == "__main__":
    print("I'm a module, can't run!")
