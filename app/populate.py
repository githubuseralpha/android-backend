import json
import datetime

from app.models import *
from app import app

@app.cli.command("test_populate")
def populate():
    db.drop_all()
    db.create_all()
    
    with open("app\\test_data\\games.json") as games_file, \
         open("app\\test_data\\users.json") as users_file, \
         open("app\\test_data\\leagues.json") as leagues_file, \
         open("app\\test_data\\groups.json") as groups_file:
        leagues = []
        for league in json.load(leagues_file):
            leagues.append(League(name=league["name"]))
            db.session.add(leagues[-1])
            
        groups = []
        for group in json.load(groups_file):
            groups.append(Group(name=group["name"], code=group["code"]))
            for league in group["leagues"]:
                filtered = [l for l in leagues if l.name==league["name"]][0]
                groups[-1].leagues.append(filtered)
            
        games = []
        for game in json.load(games_file):
            games.append(Game(team1=game["team1"], team2=game["team2"], team1_odds=game["team1_odds"],
                              team2_odds=game["team2_odds"], draw_odds=game["draw_odds"], 
                              date=datetime.datetime.strptime(game["date"], '%y-%m-%d %H:%M:%S'),
                              result=game["result"]))
            filtered = [l for l in leagues if l.name==game["league"]][0]
            filtered.games.append(games[-1])
        users = []
        for user_data in json.load(users_file):
            user = (User(login=user_data["login"], password=user_data["password"]))
            users.append(user)
            for membership in user_data["memberships"]:
                user.memberships.append(groups[membership - 1])
            db.session.add(user)
        # for bet in json.load(bets_file):
        #     user = User.query.get(bet["user_id"])
        #     game = Game.query.get(bet["game_id"])
        #     user.bets.append(game)
        #     bet = [bet for bet in user.bets.all() if bet==game][0]
        #     print(bet)
    bet = Bet(option=1, odds=2.0)
    users[0].bets.append(bet)
    games[2].bets.append(bet)

    db.session.commit()
    