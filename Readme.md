# Django python triggers PoC with Postgres

## Installation

- python 3.6.9
- binaries (postgres python3 extension) -> install_binaries.sh
- postgres 10

## Comments

- not sure which python version is in the extension

## Steps
+ install simple python function
+ install command
+ trigger (https://django-pgtrigger.readthedocs.io/en/latest/tutorial.html#keeping-a-field-in-sync-with-another)
+ install function with TD
+ load virtualenv
+ load project
+ access ORM within function
- some functions for django lookups?  
- what about async?
- consistent naming

# docs 

- often django beginners misunderstand signals concept
- add sorting example with a custom python function
- plpy example for triggers
- manage py commands
- including ORM will only work when django project is on the same host, which is rare. the only real way is to install the whole code on the db host
- there is certain danger of getting them out of hand

# todo
- finish up types mapping
