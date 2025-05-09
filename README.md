# Key Management System
### For what purpose is this Softweare ?
- Manage the possession of keys in a local Softweare

- have an overview of the deposit that has been deposited

- have a clear and traceable database that shows every step, such as who had which key and how much has been deposited

- The accounting table is used to store the deposit in compliance with the rules of double-entry bookkeeping

- Verify keys that are in use to ensure data consistency

- Flexible extensibility | the TEXT field ‘extra’ in the Keys table allows an infinite number of additional parameters through a JSON data structure

- With the option of storing a second backup path, you can set up encrypted offsite backups by transferring them to a folder in the cloud such as iCloud, Onedrive or any other mounted medium.


# Getting Started

So far this Project is not Compiled in a Installationable Medium like an .exe or .dmg 

### current way to use it!
For using this Project you need install [python](https://www.python.org) (3.13) on your System and Install the dependencies:

- [keyring](https://pypi.org/project/keyring/)
- [PyCryptodome](https://pypi.org/project/pycryptodome/)

with pip install for example in a [venv](https://docs.python.org/3/library/venv.html) 

To Clone this Code you can simply [click download this Repo as .zip](https://github.com/5463Fi-OpSour/Key-Management-System/archive/refs/heads/main.zip) 

after unpacking this zip and possible activate the venv you can start the Programm with:

``` bash
python3.13 keys_main.py
```

# Contributing

Contributions are highly welcome. 
Also especially because I Developed this Programm for a NGO.
I would be very happy if the code is only fokred or pull requests are made. Then I can also learn something from the further development

Constructive feedback or suggestions can be directed via the project’s issue tracker.
