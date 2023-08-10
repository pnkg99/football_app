# Setup

## Python Dependencies

python version : python 2.7 (python)

`pandas, googletrans`

install command : 

- `pip install pandas googletrans`

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

- precizno vreme utakmice
- first hlaf za kartone

## Error Note

`Set query rasied exception :  1364 (HY000): Field 'id' doesn't have a default value` Table does not have Auto Increment ID 