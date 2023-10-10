# Setup

## Python Dependencies

python version : python >=3.1 

dependencies install command : 

- `pip3 install pandas mysql-connector-python openpy`

## Ububtu Venv setupo script 

```sh

pip3 install pandas openpyxl mysql-connector-python openpy dotenv 

```

if that crash try update pip version

`python -m pip install --upgrade pip`

## XLSX files 

Unutar ovog direktorijuma nalaze se direktorijumi zemalja koje sadrze sledecu strukturu unutar sebe : 
* Neophodna struktura da bi program radio. unutar ovih direktorijuma nalaze se fajlovi sa xlsx extenzijom

unutar `Leagues` direktoriuma nalaze se fajlovi podataka
 - ekstenzijom `.xlsx` i brojem `id` lige na pocetku imena fajlova (tabele, mecevi i statistika lige) 
 - Drugi direktorijumi unutar kojih psotoje `Home` i `Away` direktorijumi sa xlsx fajlovima klubova. (statistika klubova)


pocetni broj imena fajlova Duela i Liga predstavljaju id za taj duel odnosno ligu

# Usage

`python3 ./program.py --help`

## history

`python3 program.py history` 

### history arguments 

- `--ctg` : inserting categories and subcateogries

- `--stat` : insert statistic for leagues, clubs and matches

- `--tbl` : insert table for leagues

- `--mtch` : insert matches  

## Nesha Standard Procedure 

0. .env configuration

1. `python3 program.py history --ctg`

2. `python3 program.py history --tbl` 

3. `python3 program.py history --mtch`

4. ! moramo da imamo fajlove klubova unutar Leagues `python3 program.py history --stat`

## Error Note

`Set query rasied exception :  1364 (HY000): Field 'id' doesn't have a default value` Table does not have Auto Increment ID 

* U direktorijumu liga duela i ekipa ne smeju da se nalaze invalidni fajlovi