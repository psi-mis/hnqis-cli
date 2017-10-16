# HNQIS User messages

> Guide on how to install the script to send user messages (attach text to DHIS2 user custom attribute)

Example message:

![](https://i.imgur.com/3MHVPR5.png)

## Installation

### on Windows
- Download and install Python 2.7 from [python.org](http://www.python.org/downloads/windows)
- Be sure to add Python 2.7 to your PATH (see here for more infos: http://docs.python-guide.org/en/latest/starting/install/win)
- Test Python in a CMD shell: `python --version` should output "Python 2.7.x"
- Update pip with `python -m pip install -U pip`
- Install _hnqis-cli_ by running `pip install hnqis-cli`
- If this throws an error that _pip_ is not installed, download and install pip from [pip.pypa.io](https://pip.pypa.io/en/stable/installing/#installing-with-get-pip-py)

### on Mac OS X & Linux
- Check if Python is installed: `python --version` should output "Python 2.7.x"
- Run `sudo -H pip install hnqis-cli`


## Usage


### 1. Get usernames

To get usernames of a userGroup, you can use the following command:

`hnqis-usergroup-usernames -s=data.psi-mis.org -u=admin -p=district -g=VC6ijypLype`

to get a CSV containing usernames of the userGroup with the UID `VC6ijypLype`. 

### 2. Adjust message

Open the CSV in e.g. Excel and put a message in the `message` column.

### 3. Send message

This CSV file can now be used to send a message:

```
username    | message
------------+------------------
user1_hnqis | Some test message
```

Get help with `hnqis-user-message --help`. An example can be

`hnqis-user-message -s=data.psi-mis.org -u=admin -p=district -c=usergroup_VC6ijypLype_users.csv`
