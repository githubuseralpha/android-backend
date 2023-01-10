import datetime
import json
import time
import requests

from . import scheduler, models, db


with open("app\\test_data\\leagues.json") as leagues_file:
    league_api_names = {}
    for league in json.load(leagues_file):
        league_api_names[league["apiId"]] = league["name"] 
        
DAYS_AHEAD = 0


@scheduler.job(seconds=10, minutes=1, hours=0)
def clean_tokens():
    print('REMOVE TOKENS')
    tokens = models.Token.query.filter(models.Token.expiration < datetime.datetime.now())
    tokens.delete()
    db.session.commit()
   
 
@scheduler.job(seconds=10, minutes=0, hours=1)
def update_matches():
    print('UPDATE MATCHES')
    date = datetime.date.today()
    url_fixtures =  f'https://v3.football.api-sports.io/fixtures?date=' + date.strftime("%Y-%m-%d")
    key = 'add14e4a8d6b3f8d81eb7677036180e8'
    host = 'v3.football.api-sports.io'
    
    fixtures_data = requests.get(url_fixtures,
                        headers={"x-rapidapi-key": key, "x-rapidapi-host": host})
    
    if not fixtures_data:
        return
    # with open("app\\sample.json") as file:
    #     data = json.load(file)
            
    fixtures_data = fixtures_data.json()
    
    games = fixtures_data["response"]
    game_query = models.Game.query.all()
    
    for game in games:
        comp = game["league"]["id"]
        if comp not in league_api_names.keys():
            continue
        api_id = game["fixture"]["id"]

        
        home_goals = game["score"]["fulltime"]["home"]
        away_goals = game["score"]["fulltime"]["away"]
        if home_goals == None:
            return

        game_inst = [game for game in game_query if game.api_id == api_id]
        if game_inst:
            if home_goals > away_goals:
                winner = 1
            elif home_goals < away_goals:
                winner = 2
            else:
                winner = 0
            game_inst[0].result = winner
            game_inst[0].team1_goals = home_goals
            game_inst[0].team2_goals = away_goals
            db.session.commit()


@scheduler.job(seconds=10, minutes=0, hours=24)
def add_matches():
    print('ADD MATCHES')
    date = datetime.date.today() + datetime.timedelta(days=DAYS_AHEAD)
    url_fixtures =  f'https://v3.football.api-sports.io/fixtures?date=' + date.strftime("%Y-%m-%d")
    url_odds =  f'https://v3.football.api-sports.io/odds?date=' + date.strftime("%Y-%m-%d")
    key = 'add14e4a8d6b3f8d81eb7677036180e8'
    host = 'v3.football.api-sports.io'
    
    odds_data = requests.get(url_odds,
                        headers={"x-rapidapi-key": key, "x-rapidapi-host": host})
    fixtures_data = requests.get(url_fixtures,
                        headers={"x-rapidapi-key": key, "x-rapidapi-host": host})
    
    if not odds_data:
        return
    # with open("app\\sample.json") as file:
    #     data = json.load(file)
            
    odds_data = odds_data.json()
    fixtures_data = fixtures_data.json()
    
    d = json.dumps(fixtures_data, indent=4)
    
    with open("app\\sample3.json", "w") as file:
        file.write(d)
    
    odds = odds_data["response"]
    games = fixtures_data["response"]
    league_query = models.League.query.all()
    game_query = models.Game.query.all()
    
    for game in games:
        comp = game["league"]["id"]
        if comp not in league_api_names.keys():
            continue
        team1 = game["teams"]["home"]["name"]
        team2 = game["teams"]["away"]["name"]
        api_id = game["fixture"]["id"]
        print(api_id)
        odd = [o for o in odds if o["fixture"]["id"] == api_id]
        team1_odds = odd[0]["bookmakers"][0]["bets"][0]["values"][0]["odd"] if odd else -1
        team2_odds = odd[0]["bookmakers"][0]["bets"][0]["values"][2]["odd"] if odd else -1
        draw_odds = odd[0]["bookmakers"][0]["bets"][0]["values"][1]["odd"] if odd else -1 
        date = datetime.date.today() + datetime.timedelta(days=DAYS_AHEAD)
        league = [l for l in league_query if l.name == league_api_names[comp]][0]
        if [game for game in game_query if game.api_id == api_id]:
            return
        new_game = models.Game(
            team1=team1,
            team2=team2,
            date=date,
            team1_odds=team1_odds,
            team2_odds=team2_odds,
            draw_odds=draw_odds,
            league=league.id,
            result=-1,
            api_id=api_id
        )
        db.session.add(new_game)
    db.session.commit()
