# Minecraft Python Utils

A Python package to help with running Bedrock Dedicated Server (BDS) on Linux (e.g. the official Bedrock server provided [here](https://www.minecraft.net/en-us/download/server/bedrock). It provides the following utilities:
* **bds-nanny**: A process nanny for BDS that gives it standardized logging and AWS CloudWatch compatible metrics, among other niceties
* **bds-console**: A CLI utility for sending commands to *bds-nanny* (without having to have the server process in your terminal foreground...)
* **bds-upgrade**: A utility to upgrade (or downgrade!) to a different BDS server version, while migrating your settings and worlds


## Setup
After checking out the package somewhere, 'cd' into the package root and run:
```
# create and activate a virtual environment (venv)
python3 -m venv .venv
. .venv/bin/activate

# install 'build' utility
pip install --upgrade build

# build the package
python -m build

# install the package:
pip install .

# install in 'development mode':
pip install --editable .
```

## Usage
TODO
