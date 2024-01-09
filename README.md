# Probely utility scripts

## Prerequisites

1. Python 3

> ℹ️  Your system may use `python` instead of `python3`, in which case modify the commands below.

2. [Pipenv](https://pypi.org/project/pipenv/) to manage dependencies and the virtualenv.

3. A Probely API token. You can get one [here](https://plus.probely.app/api-keys).

## Getting set up

```bash
pipenv install
```

## Update the schedule for all targets

This script updates all targets to have a rolling start. It excludes:

- targets that have more than one scan schedule (because we don't know which one to replace). These are logged with the word `skipping`, and should be manually checked and updated.

```bash
pipenv run ./schedule_scans_for_all_targets.py
```
