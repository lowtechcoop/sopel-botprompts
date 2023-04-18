import sys

# Ensure minimum Python version based on min reqs from pyowm
# https://pyowm.readthedocs.io/en/latest/#supported-environments-and-python-versions
if sys.version_info < (3, 7):
    raise SystemError("Sopel Bot Prompts requires Python version >= 3.7")
