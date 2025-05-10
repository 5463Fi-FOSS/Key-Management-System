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
For using this Project you need install [python](https://www.python.org) (3.13) 

"I just tried to install python for the first time on windows in the installer you have to set the two checkmarks at the bottom of the first page otherwise it won't work properly" 

on your System and Install the dependencies:

- [keyring](https://pypi.org/project/keyring/)
- [PyCryptodome](https://pypi.org/project/pycryptodome/)

with pip install for example in a [venv](https://docs.python.org/3/library/venv.html) 

To Clone this Code you can simply [click download this Repo as .zip](https://github.com/5463Fi-OpSour/Key-Management-System/archive/refs/heads/main.zip) 

after unpacking this zip and possible activate the venv you can start the Programm with:

``` bash
python3.13 keys_main.py
```

# How to use

When you Starts this Programm for the first time you have to enter a password which is longer than 16 Character to encryp the Backup with AES GCM. 

### How To Assign a Key

![Ver.1.0.0_assign_key_tab.png](https://raw.githubusercontent.com/5463Fi-OpSour/Key-Management-System/main/docs/assets/Ver.1.0.0_assign_key_tab.png)

It is rather simple to assign a key to Member you only need to now the 'Key ID' & the 'Member ID' & your own 'Member ID'.

The 'Key ID' you can fetch from the [free Keys Tab](https://github.com/5463Fi-OpSour/Key-Management-System/tree/main#free-key-tab) 
For the 'Member ID' from [Member Tab](https://github.com/5463Fi-OpSour/Key-Management-System/tree/main#member-tab)

Also you configure the 'Assigned At' whats typical the Timestamp of now

The 'Deposit Amount' and 'Remark' has a Stadard Value but you can change it free


### How to Return a Key

![Ver.1.0.0_return_key_tab.png](https://raw.githubusercontent.com/5463Fi-OpSour/Key-Management-System/main/docs/assets/Ver.1.0.0_return_key_tab.png)

The return Process is the same linke the [Assign Process](https://github.com/5463Fi-OpSour/Key-Management-System/tree/main#how-to-assign-a-key)

### Free Key Tab

![Ver.1.0.0_free_key_tab.png](https://raw.githubusercontent.com/5463Fi-OpSour/Key-Management-System/main/docs/assets/Ver.1.0.0_free_key_tab.png)

This Tab contains all Collums of the [SQLite3 schema](https://github.com/5463Fi-OpSour/Key-Management-System/tree/main/tools/keys-sqlite3.sql) without the extra Collum

for productive use, you can see all keys that are not assigned. 

### Member Tab

![Ver.1.0.0_member_tab.png](https://raw.githubusercontent.com/5463Fi-OpSour/Key-Management-System/main/docs/assets/Ver.1.0.0_member_tab.png)

In this Tab you can See All Member and which Key they have ('Key ID','Key Type'). Here are all collums from the member table are displayed witout the extra Collum [SQLite3 schema](https://github.com/5463Fi-OpSour/Key-Management-System/tree/main/tools/keys-sqlite3.sql)

### All Keys Tab

![Ver.1.0.0_all_keys_tab.png](https://raw.githubusercontent.com/5463Fi-OpSour/Key-Management-System/main/docs/assets/Ver.1.0.0_all_keys_tab.png)

Here are all Keys Displayed. That ist not only all Infos over the key also all assigment infos. 

Witout the extra Collum from Keys [SQLite3 schema](https://github.com/5463Fi-OpSour/Key-Management-System/tree/main/tools/keys-sqlite3.sql) 

### Menü

- Over The Menü you can configure the second Backup Path. For example to have an off Site Backup in the Cloud
- Over Add you can Add Member/Keys and Verify a key. [This way is not recommended at this time add this data as Insert in the DB]
- Exit is a second way to close this Programm

# Notes

The sceenshots are from MacOS so it's prettier.

There are also a few good features missing that I will add to the Isssue tracker soon

# Contributing

Contributions are highly welcome. 
Also especially because I Developed this Programm for a NGO.
I would be very happy if the code is only fokred or pull requests are made. Then I can also learn something from the further development

Constructive feedback or suggestions can be directed via the project’s issue tracker.
