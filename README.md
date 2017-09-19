# hnqis-cli [![Version](https://img.shields.io/pypi/v/hnqis-cli.svg)](https://pypi.python.org/pypi/hnqis-cli)

> Command-line scripts for **HNQIS**

* Program to Organisation Unit Assigner via CSV: `hnqis-program-orgunit --help`
* Attribute setting via CSV: `hnqis-attribute-setting --help`
* Health area indicators update (with program indicators) `hnqis-indicator-update --help`
* User messages via CSV: `hnqis-user-message --help`

### Installation / updating

* Installation with [pip](https://pip.pypa.io/en/stable/installing) (python package manager, see if it is installed: `pip -V`)
* `pip install hnqis-cli` or `sudo -H pip install hnqis-cli`
* Upgrade with `pip install hnqis-cli -U`

### Usage

* You can either pass arguments for a server / username / password or it make it read from a `dish.json` file as described in [**baosystems/dish2**](https://github.com/baosystems/dish2#configuration).
* Get help on using arguments, e.g.`hnqis-program-orgunit --help`
* In the help text, `[-v]` means an optional argument
* Logs to a file: `hnqis-cli.log`

---

#### Install from source

```
git clone --depth=1 https://github.com/psi-mis/hnqis-cli
cd hnqis-cli
python setup.py install
```

#### Source code disclaimer
- The `src/__init__.py` file was copied/modified from [dhis2-pocket-knife](https://github.com/davidhuser/dhis2-pocket-knife) (MIT licence)


#### Contribute

- Fork repo
- Install Dev requirements via `pip install -r requirements-dev.txt`
- Write a script in `src` folder, add it to `setup.py`'s `entry_points`
- Write a test in `tests`, run all tests with `python setup.py test`
- Open a Pull Request
- After merging, we do `python setup.py publish` (increase `src/__version__.py` first) to publish to PyPI

