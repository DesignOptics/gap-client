# gap-client

![Gap Solutions Logo](http://gapsolutions.dk/wp-content/uploads/2024/09/standardlogo_gapsolutions_stort-1.png)


## Introduction

This is the official Python client for [Gap Solutions](https://gapsolutions.dk/) APIs.

It is currently in heavy development, and not yet released in full version.

It is implemented as a Pyhton package, and made available on [PyPi](https://pypi.org)

Version string is stored in [VERSION](./VERSION), and used by make to correctly tag artifacts.

Requirements are managed in [requirements.in](./requirements/requirements.in) and compiled to [requirements.txt](./requirements/requirements.txt) with `make req`.


## Development

Please note that this project uses a [Makefile](./Makefile) to manage it. Simply type `make` in the project folder for help

### Set up environment

1. Install GNU make
   * NOTE: you will need gnu make. On windows, you can use [WSL](https://learn.microsoft.com/en-us/windows/wsl/about) or [gitbash](https://gitforwindows.org/)).
1. Install Python 3.9 or newer
   * NOTE: Python for windows is [here](https://www.python.org/downloads/windows/)
1. Create [virtual environment](https://docs.python.org/3/library/venv.html). (example: `python -m venv ~/my_venv`)
1. Activate virtual environment. (example: `source ~/my_venv/bin/activate`)
1. Install requirements for project: `make req`


### Test

1. Run all test: `make test`

> -- or --

1. Go to tests dir: `cd tests`
1. List available tests: `make`
1. Chose one test to run: `make gap`

> NOTE: You can find the source code for the tests [here](./tests/)

### Build

1. Change version string: `nano VERSION` *(edit and save the string)*
1. Build project package: `make pypi-build`

### Deploy

1. Make sure `PYPI_TOKEN` environment variable is set (*set in pypi.org account*)
1. Push project package to pypi: `make pypi-push`
1. Verify that the package version is uploaded to [https://pypi.org/project/gap-client/](https://pypi.org/project/gap-client/)

### Use

In your project:
1. Put `gap_client>=1.0.0` in project `requirements.txt` (*substitute the version number to the latest*)
1. Reload requirements with: `pip install -r requirements.txt`
1. Import the package with: `from gap_client import Client as gap`
1. Use the client. This example simply prints a hellp text: `print(gap.hello_gap())`

### Examples

You can find examples [here](./examples/)
