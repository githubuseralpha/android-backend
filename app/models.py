import random
import string
from . import db
from sqlalchemy.sql.functions import now

def generate_code():
    return ("".join(list(random.choice(list(string.ascii_letters)) for _ in range(16))))

memberships = db.Table('memberships',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('group_id', db.Integer, db.ForeignKey('group.id'), primary_key=True),
    db.Column('score', db.Integer)
)

league_group = db.Table('league_group',
    db.Column('league_id', db.Integer, db.ForeignKey('league.id'), primary_key=True),
    db.Column('group_id', db.Integer, db.ForeignKey('group.id'), primary_key=True)
)

league_game = db.Table('league_game',
    db.Column('league_id', db.Integer, db.ForeignKey('league.id'), primary_key=True),
    db.Column('game_id', db.Integer, db.ForeignKey('game.id'), primary_key=True)
)

    
class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    login = db.Column(db.String(100), nullable=False, unique=True)
    memberships = db.relationship('Group', secondary=memberships, lazy='subquery',
        backref=db.backref('members', lazy=True))
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
           'memberships': [membership.id for membership in self.memberships],
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
    
    @property
    def serialize(self):
        return {
           'id': self.id,
           'code': self.code,
           'leagues': [league.id for league in self.leagues],
           'members': [member.id for member in self.members]
           }
    
    def __repr__(self) -> str:
        return f'{self.id}'

class League(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable=False)
    games = db.relationship('Game', secondary=league_game, lazy='subquery',
        backref=db.backref('leagues', lazy=True))
    
    @property
    def serialize(self):
        return {
           'id': self.id,
           'name': self.name,
           'games': [game.serialize for game in self.games]
           }
    
    def __repr__(self) -> str:
        return f'{self.id} - {self.name}'

class Game(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    team1 = db.Column(db.String(100), nullable=False)
    team2 = db.Column(db.String(100), nullable=False)
    team1_odds = db.Column(db.Float, nullable=False)
    team2_odds = db.Column(db.Float, nullable=False)
    draw_odds = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime(timezone=True), server_default=now())
    result = db.Column(db.Integer, nullable=False)
    bets = db.relationship('Bet')
    
    @property
    def serialize(self):
        return {
           'id': self.id,
           'team1': self.team1,
           'team2': self.team2,
           'team1_odds': self.team1_odds,
           'team2_odds': self.team2_odds,
           'draw_odds': self.draw_odds,
           'result': self.result,
           'date': self.date
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
           'game': self.game
           }
