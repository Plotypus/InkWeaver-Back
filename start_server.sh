#!/usr/bin/env bash

# A short script to handle invocation of `server.py`.

# Find a Python 3 executable.
PYTHON="$(which python3)"

# Get this script's location.
# This invocation relies on the GNU readlink. This will not function on OS X because OS X's `readlink` does not support
# the `-f` option, so I suppress the error output.
SCRIPT=$(readlink -f "$0" 2>/dev/null)
SCRIPTDIR=$(dirname "${SCRIPT}")

# Call the script.
exec "${PYTHON}" "${SCRIPTDIR}/server.py" $@