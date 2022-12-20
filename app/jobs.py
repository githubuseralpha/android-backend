import datetime
import json
import requests

from . import scheduler, models, db

with open("app\\test_data\\leagues.json") as leagues_file:
    leagues = []
    for league in json.load(leagues_file):
        leagues.append(league["apiName"])
   
DAYS_AHEAD = 11


@scheduler.job(seconds=10, minutes=0, hours=0)
def clean_tokens():
    print('Removing')
    tokens = models.Token.query.filter(models.Token.expiration < datetime.datetime.now())
    tokens.delete()
    db.session.commit()


@scheduler.job(seconds=10, minutes=10, hours=10)
def add_matches():
    print('fetching')
    url =  f'https://footapi7.p.rapidapi.com/api/matches/{datetime.datetime.now().day + DAYS_AHEAD}/{datetime.datetime.now().month}/{datetime.datetime.now().year}'
    key = '1fd90887c0msh74d71f6c1452bcdp1bec48jsn2ba817012bc6'
    host = 'footapi7.p.rapidapi.com'
    
    data = requests.get(url,
                        headers={"X-RapidAPI-Key": key, "X-RapidAPI-Host": host})
    if not data:
        return
    
    data = data.json()
    games = data["events"]
    for game in games:
        comp = game["tournament"]["name"]
        if comp not in leagues:
            continue
        team1 = game["homeTeam"]["name"]
        team2 = game["awayTeam"]["name"]
        date = datetime.date.today() + datetime.timedelta(days=DAYS_AHEAD)
        league = models.League.query.filter_by(name=comp).first()
        games = db.session.query(models.Game).filter_by(team1=team1)
        if games.first():
            continue
        new_game = models.Game(
            team1=team1,
            team2=team2,
            date=date,
            team1_odds=1,
            team2_odds=1,
            draw_odds=1,
            league=1,
            result=league
        )
        db.session.add(new_game)
    db.session.commit()
