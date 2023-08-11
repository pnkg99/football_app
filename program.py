from scraper import *
import argparse, re

def take_xlsx_files_path(path) :
    xlsx_files_path=[]
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            if filename.endswith(".xlsx") :
                file_path = os.path.join(dirpath, filename)
                xlsx_files_path.append(file_path)
    return xlsx_files_path

def extract_league_id_from_path(file_path):
    pattern = r'\\(\d+)\s'
    match = re.search(pattern, file_path)
    if match:
        number = int(match.group(1))
        return number
    else:
        return "No numbeeer"
    
def extract_club_name_from_path(file_path) :
    last_backslash_index = file_path.rfind("\\")
    file_name = file_path[last_backslash_index + 1:]
    club_name_index = file_name.find("-")
    club_name = file_name[:club_name_index]
    return club_name

def extract_match_id_from_path(file_path):
    last_backslash_index = file_path.rfind("\\")
    file_name = file_path[last_backslash_index + 1:]
    match_name_index = file_name.find(".")
    match_index = file_name[:match_name_index]
    try : 
        match_id = int(match_index)
        return match_id
    except :
        return "No number"

if __name__ == "__main__" :
    parser = argparse.ArgumentParser()
    
    subparsers = parser.add_subparsers(title='subcommands', dest='subcommand')

    # Subparser for the "history" subcommand
    history_parser = subparsers.add_parser('history', help='Insert history for Leagues, Teams and Duels')
    history_parser.add_argument('--ctg', action='store_true', help='Insert categories and subcategories for Leagues, Clubs, Matches')
    history_parser.add_argument('--stat', action='store_true', help='Insert statistic for Leagues, Clubs, Matches')
    history_parser.add_argument('--tbl', action='store_true', help='Insert tables for Leagues')
    history_parser.add_argument('--mtch', action='store_true', help='Insert Matches for Leagues')

    args = parser.parse_args()
    
    # DB info
    psw = ''
    user = 'root'
    host = 'localhost'
    db = 'foodball_statistics_app_db'
    app = scraper(user, psw, host, db)
    
    # XLSX League Files path
    path = os.getcwd()
    liga_files = take_xlsx_files_path(os.path.join(path, "Liga"))
    ekipe_home_files = take_xlsx_files_path(os.path.join(path,"Ekipe", "HOME"))
    ekipe_away_files = take_xlsx_files_path(os.path.join(path,"Ekipe", "AWAY"))
    dueli_files = take_xlsx_files_path(os.path.join(path, "Dueli"))
    
    league_id = 1
    
    f = liga_files[0]
    
    if args.subcommand == 'history':
        if args.ctg :  
            app.insert_cateogires(f)
            app.insert_subcategories(f)
        if args.stat :
            # Insert Stat History for Leagues, Clubs and Matches
            for file in liga_files :
                league_id = extract_league_id_from_path(file)
                app.insert_league_stats_history(file, league_id)
            # Insert Clubs home and away history stats  
            for file in ekipe_home_files :
                club_name = extract_club_name_from_path(file)
                club_id = app.get_club_id(club_name)
                app.insert_clubs_stats_history(club_id,home=True, path=file)
            for file in ekipe_away_files :
                club_name = extract_club_name_from_path(file)
                club_id = app.get_club_id(club_name)
                app.insert_clubs_stats_history(club_id,home=False, path=file)            
            #Inset Matches history stats
            for file in dueli_files :
                match_id = extract_match_id_from_path(file)
                app.insert_matches_stats_history(match_id, file)
            
        if args.tbl :           
            app.insert_league_goals(f,league_id )    
            app.insert_league_corners(f, league_id)
            app.insert_league_cards_table(f, league_id)
            app.insert_league_half_table(f, league_id)

        if args.mtch :
            app.insert_matches(f, league_id)
        
    #app.update_league_goals(f, league_id)

