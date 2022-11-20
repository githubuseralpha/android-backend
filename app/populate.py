import json
import datetime

from app.models import *
from app import app

@app.cli.command("test_populate")
def populate():
    db.drop_all()
    db.create_all()
    
    with open("app\\test_data\\games.json") as games_file, \
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
            games.append(Game(team1=game["team1"], team2=game["team2"], date=datetime.datetime.strptime(game["date"], '%y-%m-%d %H:%M:%S')))
            filtered = [l for l in leagues if l.name==game["league"]][0]
            filtered.games.append(games[-1])

    db.session.commit()