import random
import string
from . import db
from sqlalchemy.sql.functions import now

def generate_code():
    return ("".join(list(random.choice(list(string.ascii_letters)) for _ in range(7))))

league_group = db.Table('league_group',
    db.Column('league_id', db.Integer, db.ForeignKey('league.id'), primary_key=True),
    db.Column('group_id', db.Integer, db.ForeignKey('group.id'), primary_key=True)
)
    
class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    login = db.Column(db.String(100), nullable=False, unique=True)
    memberships = db.relationship('Membership')
    tokens = db.relationship("Token")
    password = db.Column(db.String(50), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    bets = db.relationship('Bet')

    @property
    def serialize(self):
        return {
           'id': self.id,
           'login': self.login,
           'password': self.password,
           'memberships': [membership.group for membership in self.memberships],
           'bets': [bet.id for bet in self.bets]
           }
    
    def __repr__(self) -> str:
        return f'{self.id} - {self.login}'
    
class Group(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(10), nullable=False)
    leagues = db.relationship('League', secondary=league_group, lazy='subquery',
        backref=db.backref('groups', lazy=True))
    members = db.relationship('Membership')

    @property
    def serialize(self):
        return {
           'id': self.id,
           'code': self.code,
           'name': self.name,
           'leagues': [league.id for league in self.leagues],
           'members': [member.id for member in self.members]
           }
    
    def __repr__(self) -> str:
        return f'{self.id}'

class League(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable=False)
    games = db.relationship('Game')
    country = db.Column(db.String(100), nullable=True)
    
    @property
    def serialize(self):
        return {
           'id': self.id,
           'name': self.name,
           'games': [game.serialize for game in self.games],
           'country': self.country
           }
    
    def __repr__(self) -> str:
        return f'{self.id} - {self.name}'

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team1 = db.Column(db.String(100), nullable=False)
    team2 = db.Column(db.String(100), nullable=False)
    team1_odds = db.Column(db.Float, nullable=False)
    team2_odds = db.Column(db.Float, nullable=False)
    draw_odds = db.Column(db.Float, nullable=False)
    team1_goals = db.Column(db.Integer, nullable=True)
    team2_goals = db.Column(db.Integer, nullable=True)
    date = db.Column(db.DateTime(timezone=True), server_default=now())
    result = db.Column(db.Integer, nullable=False)
    bets = db.relationship('Bet')
    league = db.Column(db.Integer, db.ForeignKey("league.id"))
    api_id = db.Column(db.Integer, nullable=False, default=1)
    
    @property
    def serialize(self):
        return {
           'id': self.id,
           'team1': self.team1,
           'team2': self.team2,
           'team1_odds': self.team1_odds,
           'team2_odds': self.team2_odds,
           'team1_goals': self.team1_goals,
           'team2_goals': self.team2_goals,
           'draw_odds': self.draw_odds,
           'result': self.result,
           'date': self.date,
           'league': self.league,
           'country': League.query.get(self.league).country,
           'api_id': self.api_id
           }
        

class Token(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user = db.Column(db.Integer, db.ForeignKey("user.id"))
    expiration = db.Column(db.DateTime, nullable=True)
    code = db.Column(db.String(100), nullable=False)
    
    @property
    def serialize(self):
        return {
           'id': self.id,
           'user': self.user,
           'expiration': self.expiration
           }

class Bet(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user = db.Column(db.Integer, db.ForeignKey("user.id"))
    game = db.Column(db.Integer, db.ForeignKey("game.id"))
    option = db.Column(db.Integer)
    odds = db.Column(db.Float)
    date = db.Column(db.DateTime(timezone=True), server_default=now())

    @property
    def serialize(self):
        return {
           'id': self.id,
           'user': self.user,
           'game': Game.query.get(self.game).serialize,
           'option': self.option,
           'odds': self.odds,
           'date': self.date,
           }

class Membership(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user = db.Column(db.Integer, db.ForeignKey("user.id"))
    group = db.Column(db.Integer, db.ForeignKey("group.id"))
    score = db.Column(db.Float, nullable=False, default=0)
    
    @property
    def serialize(self):
        return {
           'id': self.id,
           'user': self.user,
           **Group.query.get(self.group).serialize,
           }
