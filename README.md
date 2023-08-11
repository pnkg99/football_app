# Setup

## Python Dependencies

python version : python >=3.1 

dependencies install command : 

- `pip3 install pandas googletrans mysql-connector-python openpy`

## Ububtu Venv setupo script 

```sh
#!/bin/bash

# Name of the virtual environment
venv_name="footballpy"

# Create virtual environment
python3 -m venv $venv_name

# Activate the virtual environment
source $venv_name/bin/activate

# Install packages
pip install pandas googletrans #

echo "Virtual environmentcreated and packages installed! mysql-connector-python openpy"
```

## XLSX files 

directories required for script : 

- Dueli/ 
- Ekipe/HOME/
- Ekipe/AWAY/
- Liga/

pocetni broj imena fajlova Duela i Liga predstavljaju id za taj duel odnosno ligu

# Usage

`python ./program.py --help`

## history

`python program.py history` 

### history arguments 

first time setup history insert categories and subcategories :

`python ./program.py history --ctg --stat --tbl --mtch` for inserting categories and subcateogries

- `--ctg` : inserting categories and subcateogries

- `--stat` : insert statistic for leagues, clubs and matches

- `--tbl` : insert table for leagues

- `--mtch` : insert matches 

### update

drop then insert every colum with current (active) season

## TODO

- Proveriti jos jednom da li najpreciznije ubacuje sve pdoatke

- Za meceve ubaciti future

- UPDATE 

## Error Note

`Set query rasied exception :  1364 (HY000): Field 'id' doesn't have a default value` Table does not have Auto Increment ID 