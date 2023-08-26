from scraper import *
import argparse, re, os

table_names = [
    "leagues_goals_tables",
    "leagues_goals_home_tables",
    "leagues_goals_away_tables",
    "leagues_corners_tables",
    "leagues_corners_home_tables",
    "leagues_corners_away_tables",
    "leagues_cards_tables",
    "leagues_cards_home_tables",
    "leagues_cards_away_tables",
    "leagues_goals_first_half_tables",
    "leagues_goals_second_half_tables",
    "leagues_goals_home_first_half_tables",
    "leagues_goals_home_second_half_tables",
    "leagues_goals_away_first_half_tables",
    "leagues_goals_away_second_half_tables"
]


def take_xlsx_files_path(path) :
    xlsx_files_path=[]
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            if filename.endswith(".xlsx") :
                file_path = os.path.join(dirpath, filename)
                xlsx_files_path.append(file_path)
    return xlsx_files_path
    
def extract_club_name_from_path(file_path):
    file_name = os.path.basename(file_path)
    club_name_index = file_name.find("-")
    club_name = file_name[:club_name_index]
    return club_name

def extract_match_id_from_path(file_path):
    file_name = os.path.basename(file_path)
    match_name_index = file_name.find(".")
    match_index = file_name[:match_name_index]
    try:
        match_id = int(match_index)
        return match_id
    except ValueError:
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

    update_parser = subparsers.add_parser('update', help="Update current seasson")
    update_subparsers = update_parser.add_subparsers(title='update options', dest='update_subcommand')

    update_stats_parser = update_subparsers.add_parser('stats', help='Update statistic for current seasson')
    update_stats_parser.add_argument('-l','--leagues', help='Update statistic for leagues', action="store_true")
    update_stats_parser.add_argument('-c','--clubs', help='Update statistic for clubs', action="store_true")
    update_stats_parser.add_argument('-m','--matches', help='Update statistic for matches', action="store_true")

    # Subparser for the "update players" subcommand
    update_tables_parser = update_subparsers.add_parser('tables', help='Update tables information for current seasson')
    
    update_matches_parser = update_subparsers.add_parser('matches', help='Update matches information for current seasson')
    
    args = parser.parse_args()
    
    # DB info
    psw = ''
    user = 'root'
    host = 'localhost'
    db = 'foodball_statistics_app_db'
    app = scraper(user, psw, host, db)
    
    league = "England"
    
    # XLSX League Files path
    path = os.path.join(os.getcwd(), league)
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
                filename = os.path.basename(file)
                try :
                    league_id = int(filename.split(" ")[0])
                except Exception as e :
                    print(e)
                    continue
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
            for file in liga_files :
                filename = os.path.basename(file)
                try :
                    league_id = int(filename.split(" ")[0])
                except Exception as e :
                    print(f"Wrong xlsx file format {file}",e)
                    continue       
                app.insert_league_goals(file,league_id )    
                app.insert_league_corners(file, league_id)
                app.insert_league_cards_table(file, league_id)
                app.insert_league_half_table(file, league_id)

        if args.mtch :
            app.insert_matches(f, league_id)
            
    elif args.subcommand == 'update' :
        if args.update_subcommand == 'stats' :
            if args.leagues :
                app.drop_active_seasson("leagues_stats")
                for file in liga_files :
                    filename = os.path.basename(file)
                    try :
                        league_id = int(filename.split(" ")[0])
                    except Exception as e :
                        print(f"Bad xlsx file {file}")
                        continue
                    app.update_league_statistic(file, league_id)
            if args.clubs :
                app.drop_active_seasson("clubs_home_stats")
                for file in ekipe_home_files :
                    club_name = extract_club_name_from_path(file)
                    club_id = app.get_club_id(club_name)
                    if club_id == None :
                        print(f"bad club xlsx file {file}")
                        continue
                    app.update_clubs_stats_history(club_id,home=True, path=file)
                app.drop_active_seasson("clubs_away_stats")
                for file in ekipe_away_files :
                    club_name = extract_club_name_from_path(file)
                    club_id = app.get_club_id(club_name)
                    if club_id == None :
                        print(f"bad club xlsx file {file}")
                        continue
                    app.update_clubs_stats_history(club_id,home=False, path=file)
            if args.matches :
                app.drop_active_seasson("matches_stats")
                for file in dueli_files :
                    try :
                        match_id = extract_match_id_from_path(file)
                    except :
                        print(f"bad xlsx file {file}")
                        continue
                    app.update_matches_stats_history(match_id, file)
                    
        elif args.update_subcommand == 'tables' :
            for table in table_names :
                app.drop_active_seasson(table=table)
            for file in liga_files :
                filename = os.path.basename(file)
                try :
                    league_id = int(filename.split(" ")[0])
                except Exception as e :
                    print(e)
                    continue 
                app.update_table_goals(file,league_id )    
                app.update_table_corners(file, league_id)
                app.update_table_cards(file, league_id)
                app.update_table_half(file, league_id)
                
        elif args.update_subcommand == 'matches' :
            app.update_matches(f, league_id)
        else :
            print("Provide update subcommand")
    #app.update_league_goals(f, league_id)

