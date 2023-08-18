import io, pandas as pd, mysql.connector, time
from googletrans import Translator

# 2019-2027
SEASON_TABLE = "seasons"

# tables
categories_tables = ["leagues_stats_categories","matches_stats_categories", "clubs_stats_categories"]
subcategories_tables = ["leagues_stats_subcategories","matches_stats_subcategories", "clubs_stats_subcategories"] 

CLUBS_HOME_STATS_TABLE = "clubs_home_stats"
CLUBS_AWAY_STATS_TABLE = "clubs_away_stats"

# 1-17
LEAGUE_SUBCATEGORIES_TABLE = "leagues_stats_subcategories"
LEAGUE_STATS_TABLE = "leagues_stats"
LEAGUE_CATEGORIES_TABLE = "leagues_stats_categories"
# T-G
LEAGUE_GOALS_TABLE = "leagues_goals_tables"
LEAGUE_GOALS_HOME_TABLE = "leagues_goals_home_tables"
LEAGUE_GOALS_AWAY_TABLE = "leagues_goals_away_tables"
# T-C
LEAGUE_CORNERS_TABLE = "leagues_corners_tables"
LEAGUE_CORNERS_HOME_TABLE = "leagues_corners_home_tables"
LEAGUE_CORNERS_AWAY_TABLE = "leagues_corners_away_tables"
# T Card
LEAGUE_CARDS_TABLE = "leagues_cards_tables"
LEAGUE_CARDS_HOME_TABLE = "leagues_cards_home_tables"
LEAGUE_CARDS_AWAY_TABLE = "leagues_cards_away_tables"
# T-Half 
LEAGUES_GOALS_FIRST_HALF_TABLES="leagues_goals_first_half_tables"
LEAGUES_GOALS_SECOND_HALF_TABLES="leagues_goals_second_half_tables"
LEAGUES_GOALS_HOME_FIRST_HALF_TABLES="leagues_goals_home_first_half_tables"
LEAGUES_GOALS_HOME_SECOND_HALF_TABLES="leagues_goals_home_second_half_tables"
LEAGUES_GOALS_AWAY_FIRST_HALF_TABLES = "leagues_goals_away_first_half_tables"
LEAGUES_GOALS_AWAY_SECOND_HALF_TABLES="leagues_goals_away_second_half_tables"

CLUBS_TABLE = "clubs"

MATCHES_TABLE = "matches"

class mysqldb :
    def __init__(self, user, password, host, database):
        self.cnx = mysql.connector.connect(user=user, password=password, host=host, database=database)
        self.cursor = self.cnx.cursor(buffered=True)
        
    def get_one_row(self, query) :
        try:
            self.cursor.execute(query)
            result = self.cursor.fetchone()
            return result[0]
        except:
            return None
        
    def set_query(self, query) : 
        self.cursor.execute(query)
        self.cnx.commit()       


class scraper(mysqldb) :
    def __init__(self, user, password, host, database):
        mysqldb.__init__(self, user, password, host, database)
        self.w = Translator()
        self.trns_off = True
        
    
    def read_xlsx_simple(self, path, sheet) :
        buffer = io.StringIO()
        df = pd.read_excel(path, sheet_name=str(sheet))
        df.to_csv(buffer, index=False)
        buffer.seek(0)        
        df = pd.read_csv(buffer, header=None)
        df = df.fillna('')
        return df
    
    def read_xlsx_file_sheet(self, file_path, sheet, lb=0, ub=None, skiprows=1, nrows=300) :
        buffer = io.StringIO()
        
        
        sheet_df = pd.read_excel(file_path, sheet_name=str(sheet), nrows=1)
        max_columns = sheet_df.shape[1]
        
        if ub is None or ub > max_columns :
            ub = max_columns
        
        df = pd.read_excel(file_path, sheet_name=str(sheet), usecols=range(lb, ub), skiprows=skiprows, nrows=nrows, header=0 )
        df.to_csv(buffer, index=False)
        buffer.seek(0)        
        df = pd.read_csv(buffer, header=None)
        df = df.fillna('')
        return df
    
    def translate(self, string):
        if self.trns_off : 
            return "NOT SET"
        try :
            return self.translator.translate( string, dest='en').text
        except :
            return "NOT SET"
    
    # GET ID's from 
    
    def get_season_id(self, season):
        query = f"SELECT id FROM seasons WHERE name = '{season}'"
        return self.get_one_row(query)
    
    def get_active_season_name(self) :
        query ="SELECT name FROM seasons WHERE active = 1"
        return self.get_one_row(query)

    def get_active_season_id(self) :
        query ="SELECT id FROM seasons WHERE active = 1"
        return self.get_one_row(query)
    
    def get_subcategory_id(self, subcategory) :
        query = f"SELECT id FROM {LEAGUE_SUBCATEGORIES_TABLE} WHERE name_sr = '{subcategory}'"
        return self.get_one_row(query)

    def get_category_id(self, category) :
        query = f"SELECT id FROM {LEAGUE_CATEGORIES_TABLE} WHERE name_sr = '{category}'"
        category = self.get_one_row(query)
        return category
    
    def get_club_id(self, club_name) :
        query = f"SELECT id FROM {CLUBS_TABLE} WHERE excel_name = '{club_name}'"
        category = self.get_one_row(query)        
        return category
    
    def get_club_name(self, club_id) :
        query = f"SELECT excel_name FROM {CLUBS_TABLE} WHERE id = {club_id}"
        club_name = self.get_one_row(query)        
        return club_name
        
    ## INJECT INTO MYSQL TABLES

    # insert categories 1-17 for league, duels and teams
    def insert_cateogires(self, path) :
        # Od 1 do 17 papira
        for category_id in range(1, 18): 
            # Uzmi samo prve dve kolone prve sezone, dovoljno da prepoznamo sve kategorije papira
            df = self.read_xlsx_file_sheet(path, sheet=category_id, lb=0, ub=2)
            category_sr = df.iloc[2,1]
            categor_en = self.translate(category_sr)
            # Napravi SQL upite
            for ctg_table in categories_tables :
                getq = f"SELECT * FROM {ctg_table} WHERE name_sr = '{category_sr}'"
                setq = f'INSERT INTO {ctg_table} (name_sr, name_en, status, created_at, updated_at) VALUES ("{category_sr}", "{categor_en}", 1, NOW(), NOW())'
                out = self.get_one_row(getq)
                if out == None :
                    try : 
                        print(setq)
                        self.set_query(setq)
                    except Exception as e :
                        print("Category set for {ctg_table} failed : ", e )
                
    # insert subcategories 1-17 for league, duels and teams
    def insert_subcategories(self, path) :
        for category_id in range(1, 18): 
            df = self.read_xlsx_file_sheet(path, sheet=category_id, lb=1, ub=3, skiprows=3)
            category = df.iloc[0,0]
            category_id = self.get_category_id(category)
            for i,row in df.iterrows():
                if row[0] != '' and (row[1] == '0' or row[1] == ''):
                    subcategory_sr = row[0]
                    subcategory_en = self.translate(subcategory_sr)
                    values = f'"{category_id}", "{subcategory_sr}","{subcategory_en}", 1, NOW(), NOW()'        
                    for table in subcategories_tables :
                            id_field = table[:-1] + "_id"
                            index = id_field.find("_")
                            index = id_field.find("_", index + 1)
                            first_part = id_field[:index]
                            second_part = id_field[index:]
                            second_part = "_" + second_part[4:]
                            id_field = first_part + second_part
                            getq = f"SELECT * FROM {table} WHERE name_sr = '{subcategory_sr}'"   
                            setq = f'INSERT INTO {table} ({id_field}, name_sr, name_en, status, created_at, updated_at) VALUES ({values})'
                            out = self.get_one_row(getq)
                            if out == None :
                                try :
                                    print(setq)
                                    self.set_query(setq)
                                except Exception as e : 
                                    print(e)

    # LEAGUES STATS
    def insert_league_stats_history(self, path, league_id) :
        for sheet in range(1, 18):
            sheet_datasets=0
            lower_bound = 1 
            upper_bound = 7
            print("Sheet : ", sheet)
            while True :
                df = self.read_xlsx_file_sheet(path, sheet, lower_bound, upper_bound)
                try :
                    season = df.iloc[0,0].split(' ')[1]
                    season_id = self.get_season_id(season)
                except Exception as e :
                    print(e)
                    lower_bound+=6
                    upper_bound+=6
                    continue
                active_seasson_id = self.get_active_season_id()
                if season_id == None :
                    break
                if season_id > active_seasson_id :
                    break
                print(f"Inserting history stats for league with id : {league_id} for {season} Seasson ")
                datasets = 0
                for row_index,row in df.iterrows():
                    if row_index == 0 :
                        continue
                    if row[0] != '' and (row[1] == '' or row[1] =="0")  :
                        subcategory_sr = row[0]
                        subcategory_id = self.get_subcategory_id(subcategory_sr)                        
                    elif row[0] != '' and row[1] != '' :
                        game_sr = row[0]
                        game_en = self.translate(game_sr)
                        game_description_sr = row[1]
                        game_description_en = self.translate(game_description_sr)
                        gw = row[2]
                        mp = row[3]
                        percent = row[4]
                        status =1
                        percent = round(float(percent)*100, 2)
                        values = f'"{league_id}", "{season_id}","{subcategory_id}","{game_sr}", "{game_en}","{game_description_sr}", "{game_description_en}","{gw}", "{mp}", "{percent}", {status}, NOW(), NOW()'
                        query = f'INSERT INTO leagues_stats (league_id, season_id,leagues_stats_subcategorie_id, game_sr,game_en,game_description_sr,game_description_en, GW, MP, percent,status, created_at, updated_at) VALUES ({values})'
                        try :
                            self.set_query(query)
                            datasets+=1
                        except Exception as e :
                            print("Set query rasied exception : ", e)       
                    else :
                        pass 
                lower_bound+=6
                upper_bound+=6
                sheet_datasets+=datasets
            print(f"{sheet_datasets} datasets, Sheet : {sheet} - Season : {season}")
                
    # CLUBS STATS
    def insert_clubs_stats_history(self,club_id,home, path) :
        club_name = self.get_club_name(club_id)
        if home :
            table = CLUBS_HOME_STATS_TABLE
        else :
            table = CLUBS_AWAY_STATS_TABLE
            
        for sheet in range(1, 18):
            sheet_datasets = 0
            lower_bound = 49
            upper_bound =  55
            print("Sheet : ", sheet)
            while True :
                df = self.read_xlsx_file_sheet(path, sheet, lower_bound, upper_bound)
                try :
                    season = df.iloc[0,0].split(' ')[1]
                    season_id = self.get_season_id(season)
                except Exception as e :
                    print(e)
                    lower_bound+=6
                    upper_bound+=6
                    continue
                active_season_id = self.get_active_season_id()

                if season_id == None :
                    print("Exit due to season not found", season)
                    continue
                if season_id > active_season_id :
                    print("Break from higher season")
                    break
                
                print(f"Inserting stats history for {club_name} season {season} ")
                datasets = 0
                for row_index,row in df.iterrows():
                    if row_index == 0 :
                        continue
                    if row[0] != '' and (row[1] == '' or row[1] =="0")  :
                        subcategory_sr = row[0]
                        clubs_stats_subcategorie_id = self.get_subcategory_id(subcategory_sr)                        
                    elif row[0] != '' and row[1] != '' :
                        game_sr = row[0]
                        game_en = self.translate(game_sr)
                        game_description_sr = row[1]
                        game_description_en = self.translate(game_description_sr)
                        gw = row[2]
                        mp = row[3]
                        percent = row[4]  
                        percent = round(float(percent)*100, 2)    
                        values = f'"{club_id}", "{season_id}","{clubs_stats_subcategorie_id}","{game_sr}", "{game_en}","{game_description_sr}", "{game_description_en}","{gw}", "{mp}", "{percent}", 1, NOW(), NOW()'
                        query = f'INSERT INTO {table} (club_id, season_id,clubs_stats_subcategorie_id, game_sr,game_en,game_description_sr,game_description_en, GW, MP, percent,status, created_at, updated_at) VALUES ({values})'
                        try :
                            self.set_query(query)
                            datasets+=1
                        except Exception as e :
                            print(df)
                            exit()
                            print("Set query rasied exception : ", e)  
                    else : 
                        pass
                lower_bound+=6
                upper_bound+=6
                sheet_datasets+=datasets
            print(f"{sheet_datasets} number of datasets {club_name} - Sheet : {sheet} - Season : {season}")
                
    # MATCHES STATS
    def insert_matches_stats_history(self, match_id, path) :            
        for sheet in range(1, 18):
            sheet_datasets =0
            lower_bound = 49
            upper_bound = 55
            print("Sheet : ", sheet)
            list = [13,14,15]
            if sheet in list :
                lower_bound = 37
                upper_bound = 43
            while True :
                df = self.read_xlsx_file_sheet(path, sheet, lower_bound, upper_bound)
                try :
                    season = df.iloc[0,0].split(' ')[1]
                    season_id = self.get_season_id(season)
                except Exception as e :
                    print(e)
                    lower_bound+=6
                    upper_bound+=6
                active_season_id = self.get_active_season_id()
                if season_id == None :
                    break
                if season_id > active_season_id :
                    break
                datasets=0
                for row_index,row in df.iterrows():
                    if row_index == 0 :
                        continue
                    if row[0] != '' and (row[1] == '' or row[1] =="0")  :
                        subcategory_sr = row[0]
                        matches_stats_subcategorie_id = self.get_subcategory_id(subcategory_sr)                        
                    elif row[0] != '' and row[1] != '' :
                        game_sr = row[0]
                        game_en = self.translate(game_sr)
                        game_description_sr = row[1]
                        game_description_en = self.translate(game_description_sr)
                        gw = row[2]
                        mp = row[3]
                        percent = row[4]      
                        percent = round(float(percent)*100, 2)
                        values = f'"{match_id}", "{season_id}","{matches_stats_subcategorie_id}","{game_sr}", "{game_en}","{game_description_sr}", "{game_description_en}","{gw}", "{mp}", "{percent}", 1, NOW(), NOW()'
                        query = f'INSERT INTO matches_stats (match_id, season_id,matches_stats_subcategorie_id, game_sr,game_en,game_description_sr,game_description_en, GW, MP, percent,status, created_at, updated_at) VALUES ({values})'

                        try :
                            self.set_query(query)
                            datasets+=1
                        except Exception as e :
                            print("Set query rasied exception : ", e)
                            break   
                    else :
                        pass 
                lower_bound+=6
                upper_bound+=6
                sheet_datasets+=datasets
            print(f"{sheet_datasets} datasets Match : {match_id} - Sheet : {sheet} - Season :")
                  
        ####    LEAGUE  ####
        ####    TABLES  ####
                    
    ### T-G ### Table - Goals

    def insert_league_goals(self,file,league_id) :
        lb = 1
        ub = 14
        while True : 
            print(ub, lb)
            try :
                df = self.read_xlsx_file_sheet(file, "T-G", lb=lb, ub=ub, nrows=72)
            except Exception as e :
                print("df ", e)
                break;
            try :
                season = df.iloc[0,0].split(' ')[1]
                season_id = self.get_season_id(season)
            except Exception as e :
                print("Cant find seasson", e)
                break
            active_season_id = self.get_active_season_id()
            if season_id == None :
                break
            if season_id > active_season_id :
                break
            for row_index,row in df.iterrows():
                if 24 > row_index > 3 :
                    table = LEAGUE_GOALS_TABLE
                elif 47 > row_index > 26 :
                    table = LEAGUE_GOALS_HOME_TABLE
                elif 70 > row_index > 49 :
                    table = LEAGUE_GOALS_AWAY_TABLE
                else :
                    continue
                rank = row[0]
                club_name = row[1]
                club_id = self.get_club_id(club_name)
                if club_id == None :
                            continue
                values = f'{league_id},"{season_id}", "{rank}", "{club_id}", "{row[6]}", "{row[7]}", "{row[8]}", "{row[9]}", "{row[10]}", "{row[11]}", "{row[12]}", NOW(), NOW()'
                q = f'INSERT INTO {table} (league_id, season_id, rank, club_id, Pts, GP, W, D, L, GF, GA, created_at, updated_at) VALUES ({values})'
                try :
                    self.set_query(q)
                    print(q)
                except Exception as e :
                       print("Query exception", e)
                       pass
            ub+=14
            lb+=14
                         

    ### T-C ### Table - Corners

    def insert_league_corners(self,file, league_id) :
        lb = 1
        ub = 12
        while True :
            try :     
                df = self.read_xlsx_file_sheet(file, "T-C", lb=lb, ub=ub,nrows=73)
            except Exception as e :
                print(e)
                break
            try :
                season = df.iloc[0,0].split(' ')[1]
                season_id = self.get_season_id(season)
            except Exception as e :
                print("Cant find seasson", e)
                break
            active_season_id = self.get_active_season_id()
            if season_id == None :
                break 
            if season_id > active_season_id :
                break                                      
            for row_index,row in df.iterrows():
                if 25 > row_index > 4 :
                    table = LEAGUE_CORNERS_TABLE
                elif 49 > row_index > 28 :
                    table = LEAGUE_CORNERS_HOME_TABLE
                elif 74 > row_index > 52 :
                    table = LEAGUE_CORNERS_AWAY_TABLE
                else :
                    continue
                
                try :
                    rank = row[0]
                    club_name = row[1]
                    club_id = self.get_club_id(club_name)
                    if club_id == None :
                        continue
                    values = f'{league_id},"{season_id}", "{rank}", "{club_id}", "{row[6]}", "{row[7]}", "{row[8]}", "{row[9]}", "{row[10]}", NOW(), NOW()'
                    q = f'INSERT INTO {table} (league_id, season_id, rank, club_id, GP, FT_CF, FT_CA, HT_CF, HT_CA, created_at, updated_at) VALUES ({values})'
                    print(q)
                    self.set_query(q)
                except Exception as e:
                    print(e)
                    break
            ub+=12
            lb+=12
    
    ### T Cards ### Table - Cards

    def insert_league_cards_table(self,file, league_id) :
        lb = 1
        ub = 12
        while True :
            try:   
                df = self.read_xlsx_file_sheet(file, "T Card", lb=lb, ub=ub,nrows=75)
            except Exception as e :
                print(e)
                break
            try :
                season = df.iloc[0,0].split(' ')[1]
                season_id = self.get_season_id(season)
            except Exception as e :
                print("Cant find seasson", e)
                break
            active_season_id = self.get_active_season_id()
            if season_id == None :
                break   
            if season_id > active_season_id :
                break
            for row_index,row in df.iterrows():
                if 25 > row_index >= 5 :
                    table =  LEAGUE_CARDS_TABLE
                elif 49 > row_index >= 29 :
                    table = LEAGUE_CARDS_HOME_TABLE
                elif 73 >= row_index >= 53 :
                    table = LEAGUE_CARDS_AWAY_TABLE
                else :
                    continue
                try:
                    rank = row[0]
                    club_name = row[1]
                    club_id = self.get_club_id(club_name)
                    if club_id == None :
                        continue
                    values = f'{league_id},"{season_id}", "{rank}", "{club_id}", "{row[6]}", "{row[7]}", "{row[8]}", "{row[9]}", "{row[10]}", NOW(), NOW()'
                    q = f'INSERT INTO {table} (league_id, season_id, rank, club_id, GP, YCF, YCA, RCF, RCA, created_at, updated_at) VALUES ({values})'
                    print(q)
                    self.set_query(q)
                except Exception as e :
                    print(e)
                    break        
            ub+=12
            lb+=12

    ### T-Half ###  Table - HalfTime
    
    def insert_league_half_table(self,file, league_id) :
        lb = 1
        ub = 13
        while True : 
            try :     
                df = self.read_xlsx_file_sheet(file, "T-Half", lb=lb, ub=ub, nrows=150)
            except Exception as e :
                print(e)
                break
            try :
                season = df.iloc[0,0].split(' ')[1]
                season_id = self.get_season_id(season)
            except Exception as e :
                print("Cant find seasson", e)
                break
            active_season_id = self.get_active_season_id()
            if season_id == None :
                break  
            if season_id > active_season_id :
                break
            print(ub, lb)      
            for row_index,row in df.iterrows():
                if 25 > row_index > 4 :
                    table = LEAGUES_GOALS_FIRST_HALF_TABLES
                elif 49 > row_index > 28 :
                    table = LEAGUES_GOALS_SECOND_HALF_TABLES
                elif 73 > row_index > 52 :
                    table = LEAGUES_GOALS_HOME_FIRST_HALF_TABLES
                elif 97 > row_index > 76 :
                    table = LEAGUES_GOALS_HOME_SECOND_HALF_TABLES
                elif 121 > row_index > 100 :
                    table = LEAGUES_GOALS_AWAY_FIRST_HALF_TABLES
                elif 145 > row_index > 124 :
                    table = LEAGUES_GOALS_AWAY_SECOND_HALF_TABLES
                else :
                    continue
                try :
                    rank = row[0]
                    club_name = row[1]
                    club_id = self.get_club_id(club_name)
                    if club_id == None :
                        continue
                    values = f'{league_id},"{season_id}", "{rank}", "{club_id}", "{row[6]}", "{row[7]}", "{row[8]}", "{row[9]}", "{row[10]}", "{row[11]}", NOW(), NOW()'
                    q = f'INSERT INTO {table} (league_id, season_id, rank, club_id, GP, W, D, L, GF, GA, created_at, updated_at) VALUES ({values})'
                    print(q)
                    self.set_query(q)
                except Exception as e :
                    print(e)
                    print("Row index : ",row_index)
                    break
            ub+=13
            lb+=13
            
    def insert_matches(self, file, league_id) :
        lb_col_goals = 1
        ub_col_goals = 8
        lb_col_corners = 1
        ub_col_corners = 9
        lb_col_red = 1
        ub_col_red = 6
        lb_col_yellow = 1
        ub_col_yellow = 7
       
        skip_rows_goals = 10
        
        number_of_cols = self.read_xlsx_file_sheet(file, "Goals").shape[1] # Horizontal number of cells
        number_of_rows = self.read_xlsx_file_sheet(file, "Goals", nrows=550).shape[0] # Vertical number of cells
        live_matches = False
        while number_of_cols >= ub_col_goals : # Itterate by each season
            # GEt Season ID 
            df = self.read_xlsx_file_sheet(file, "Goals", lb=lb_col_goals, ub=ub_col_goals, nrows=1, skiprows=3)
            first_cell = df.iloc[0,0]
            season = first_cell.split(' ')[1]
            season_id = self.get_season_id(season)
            print(season, season_id)
            if season_id <=3 :
                status = 1
            if season_id == None :
                break
            active_season_id = self.get_active_season_id()
            status = -1
            if season_id == active_season_id :
                status = 0
                try :
                    fixdf = self.read_xlsx_simple(file, "Fix")
                except Exception as e :
                    print(e)
            if season_id == None :
                break
            print(f"Inserting matches for league with id {league_id} for {season} Seasson ")
            lb_row_goals = 11
            # Iterrate by colums 
            while lb_row_goals < number_of_rows :
                df = self.read_xlsx_file_sheet(file, "Goals", lb=lb_col_goals, ub=ub_col_goals, nrows=skip_rows_goals, skiprows=lb_row_goals)
                df1 = self.read_xlsx_file_sheet(file, "Corners", lb=lb_col_corners, ub=ub_col_corners, nrows=skip_rows_goals, skiprows=lb_row_goals)
                df2 = self.read_xlsx_file_sheet(file, "Red cards", lb=lb_col_red, ub=ub_col_red, nrows=skip_rows_goals, skiprows=lb_row_goals)
                df3 = self.read_xlsx_file_sheet(file, "Yellow cards", lb=lb_col_yellow, ub=ub_col_yellow, nrows=skip_rows_goals, skiprows=lb_row_goals)
                for index, row in df.iterrows():
                    if index == 0 :
                        try :
                            round = df.iloc[0,0]
                            round = float(round)
                            round = int(round)
                            print("Round: ", round)
                            continue
                        except Exception as e :
                            print(e)
                            print(round, type(round))
                            exit()
                    else :
                        home_name = row[0]
                        status = -1
                        if home_name == 0  :
                            found_round = False
                            counter = 0
                            for index, row in fixdf.iterrows() :
                                if counter >= 10 :
                                    break
                                if found_round :
                                    date = row[1]
                                    home_name = row[2]
                                    away_name = row[4]
                                    home_id = self.get_club_id(home_name)
                                    if home_id == None :
                                        continue
                                    away_id = self.get_club_id(away_name)
                                    parameters = '(league_id, season_id, round, home_name, away_name, home_id, away_id, ht_score, ft_score, ht1_home_goals, ht1_away_goals, ht2_home_goals, ht2_away_goals, ht1_home_corners, ht1_away_corners, ht2_home_corners, ht2_away_corners, ht1_home_cards_red, ht1_away_cards_red, ht2_home_cards_red, ht2_away_cards_red, ht1_home_cards_yellow, ht1_away_cards_yellow, ht2_home_cards_yellow, ht2_away_cards_yellow, datetime_game, status, created_at, updated_at)'
                                    values = f'({league_id}, {season_id}, {round}, \'{home_name}\', \'{away_name}\', {home_id}, {away_id}, "", "", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, \'{date}\', {status}, NOW(), NOW())'
                                    cmd = f'INSERT INTO matches {parameters} VALUES {values}'
                                    try :
                                        self.set_query(cmd)
                                        print(cmd)
                                        counter+=1
                                    except Exception as e :
                                        print(e, cmd)
                                elif row[1] == "ROUND" :
                                    next_row = fixdf.iloc[index + 1]
                                    round_num_str = next_row[1]
                                    try:
                                        round_num = int(round_num_str)
                                        if round_num == round:
                                            found_round = True
                                            print("Found round", round_num)
                                    except Exception as e:
                                        print(e)
                            break
                        else :
                            try: 
                                away_name = row[1]                
                                home_id = self.get_club_id(home_name)
                                away_id = self.get_club_id(away_name)
                                ht_score = f'{row[2]} - {row[3]}'
                                f_score = f'{row[4]} - {row[5]}'
                                ht1_home_goals = row[2]
                                ht1_away_goals = row[3]
                                ht2_home_goals = int(row[4]) - int(row[2])
                                ht2_away_goals = int(row[5]) - int(row[3])
                                datetime_game = row[6]
                                status = 1
                                for index, row1 in df1.iterrows():
                                    if row1[0] == home_name and row1[1] == away_name :                         
                                        ht1_home_corners = row1[2]
                                        ht2_home_corners = int(row1[4]) - int(row1[2])
                                        ht1_away_corners = row1[3]
                                        ht2_away_corners = int(row1[5]) - int(row1[3])
                                for index, row2 in df2.iterrows():
                                    if row2[0] == home_name and row2[1] == away_name :                      
                                        ht1_home_cards_red = 0
                                        ht2_home_cards_red = row2[2]
                                        ht1_away_cards_red = 0
                                        ht2_away_cards_red = row2[3]
                                for index, row3 in df3.iterrows():
                                    if row3[0] == home_name and row3[1] == away_name :                             
                                        ht1_home_cards_yellow = 0
                                        ht2_home_cards_yellow = row3[2]
                                        ht1_away_cards_yellow = 0
                                        ht2_away_cards_yellow = row3[3]          
                                values = f'{league_id}, "{season_id}", "{round}", "{home_name}", "{away_name}", "{home_id}", "{away_id}", "{ht_score}", "{f_score}", "{ht1_home_goals}", "{ht1_away_goals}", "{ht2_home_goals}", "{ht2_away_goals}", "{ht1_home_corners}", "{ht1_away_corners}", "{ht2_home_corners}", "{ht2_away_corners}", "{ht1_home_cards_red}", "{ht1_away_cards_red}", "{ht2_home_cards_red}", "{ht2_away_cards_red}", "{ht1_home_cards_yellow}", "{ht1_away_cards_yellow}", "{ht2_home_cards_yellow}", "{ht2_away_cards_yellow}", "{datetime_game}",{status}, NOW(), NOW()'
                                q = f'INSERT INTO {MATCHES_TABLE} (league_id, season_id, round, home_name, away_name, home_id, away_id, ht_score, ft_score, ht1_home_goals, ht1_away_goals, ht2_home_goals, ht2_away_goals, ht1_home_corners, ht1_away_corners, ht2_home_corners, ht2_away_corners, ht1_home_cards_red, ht1_away_cards_red, ht2_home_cards_red, ht2_away_cards_red, ht1_home_cards_yellow, ht1_away_cards_yellow, ht2_home_cards_yellow, ht2_away_cards_yellow, datetime_game, status, created_at, updated_at) VALUES ({values})'
                                self.set_query(q)
                                print(q)
                            except Exception as e :
                                print(e, q)
                lb_row_goals +=14
            lb_col_corners+=9
            ub_col_corners+=9
            lb_col_goals += 8
            ub_col_goals += 8
            lb_col_red +=6
            ub_col_red +=6
            lb_col_yellow+=7
            ub_col_yellow+=7


# Matches

# GOALS_TABLE
# CORNERS_TABLE
# YELLOW_CARDS_TABLE
# RED_CARDS_TABLE



            
 