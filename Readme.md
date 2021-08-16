# Django python triggers PoC with Postgres

## Installation

- python 3.6.9
- binaries (postgres python3 extension) -> setup.sh
- postgres 10

## Steps
+ install simple python function
+ install command
+ trigger (https://django-pgtrigger.readthedocs.io/en/latest/tutorial.html#keeping-a-field-in-sync-with-another)
+ install function with TD
+ load virtualenv
+ load project
+ access ORM within function
+ some functions for django lookups?  
- consistent naming

# docs 

- about python versions in postgres
- how the code is installed
- often django beginners misunderstand signals concept
- add sorting example with a custom python function
- plpy example for triggers
- manage py commands
- including ORM will only work when django project is on the same host, which is rare. the only real way is to install the whole code on the db host
- there is certain danger of getting them out of hand

# todo
- finish up types mapping
