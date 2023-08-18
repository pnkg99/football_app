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
pip3 install pandas googletrans mysql-connector-python openpy #

echo "Virtual environmentcreated and packages installed! "
```

## XLSX files 

Unutar ovog direktorijuma nalaze se direktorijumi zemalja koje sadrze sledecu strukturu unutar sebe : 
* Neophodna struktura da bi program radio. unutar ovih direktorijuma nalaze se fajlovi sa xlsx extenzijom

- Dueli/ 
- Ekipe/HOME/
- Ekipe/AWAY/
- Liga/

pocetni broj imena fajlova Duela i Liga predstavljaju id za taj duel odnosno ligu

# Usage

`python3 ./program.py --help`

## history

`python3 program.py history` 

### history arguments 

first time setup history insert categories and subcategories :

`python3 ./program.py history --ctg --stat --tbl --mtch` for inserting categories and subcateogries

- `--ctg` : inserting categories and subcateogries

- `--stat` : insert statistic for leagues, clubs and matches

- `--tbl` : insert table for leagues

- `--mtch` : insert matches  

## Error Note

`Set query rasied exception :  1364 (HY000): Field 'id' doesn't have a default value` Table does not have Auto Increment ID 

* U direktorijumu liga duela i ekipa ne smeju da se nalaze invalidni fajlovi