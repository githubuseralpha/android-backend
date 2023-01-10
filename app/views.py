import datetime
import json
from flask import (
    Blueprint, Response, jsonify, request
)

from . import db, models

bp = Blueprint('bp', __name__, url_prefix='/')

def jsonify_row(row, keys):
    result = []
    for item in row:
        result.append({
            key: item[i] for i, key in enumerate(keys)
        })
    return jsonify(result)

def get_user(code):
    token = models.Token.query.filter(models.Token.code==code).first()
    if not token: return None
    user = token.user
    return user


@bp.route('/users', methods=('GET',))
def users():
    query = models.User.query.all()
    return jsonify([user.serialize for user in query])


@bp.route('/leagues', methods=('GET',))
def leagues():
    query = models.League.query.all()
    return jsonify([league.serialize for league in query])


@bp.route('/games', methods=('GET',))
def games():
    query = models.Game.query.all()
    return jsonify([game.serialize for game in query])

@bp.route('/bets', methods=('GET',))
def bets():
    query = models.Bet.query.all()
    return jsonify([bet.serialize for bet in query])

@bp.route('/group/<int:id>', methods=('GET',))
def group(id):
    query = models.Group.query.get(id)
    return jsonify(query.serialize)

@bp.route('/games-by-league/<int:id>', methods=('GET',))
def games_by_league(id):
    query = models.League.query.get(id).games
    return jsonify([game.serialize for game in query])

@bp.route('/groups-by-user/<int:id>', methods=('GET',))
def group_by_user(id):
    query = models.User.query.get(id).memberships
    return jsonify([group.serialize for group in query])

@bp.route('/users-by-group/<int:id>', methods=('GET',))
def users_by_group(id):
    query = models.Group.query.get(id).members
    return jsonify([models.User.query.get(membership.user).serialize for membership in query])

@bp.route('/users-rank/<int:id>', methods=('GET',))
def users_rank(id):
    query = models.Group.query.get(id).members
    query = sorted(query, key=lambda x: x.score)
    data = []
    for membership in query:
        x = models.User.query.get(membership.user).serialize
        data.append({'login':  x['login'], 'id':  x['id'], 'score':  membership.score})
    return jsonify(data)

@bp.route('/user/<int:id>', methods=('GET',))
def user(id):
    query = models.User.query.get(id)
    return jsonify(query.serialize)

@bp.route('/game/<int:id>', methods=('GET',))
def game(id):
    query = models.Game.query.get(id)
    return jsonify(query.serialize)

@bp.route('/bet/<int:id>', methods=('GET',))
def bet(id):
    query = models.Bet.query.get(id)
    return jsonify(query.serialize)

@bp.route('/post-bet', methods=('POST',))
def post_bet():
    request_data = request.get_json()
    user = request_data['user']
    game = request_data['game']
    option = request_data['option']  
    if option == 1:
        odds = models.Game.query.get(game).team1_odds
    elif option == 2:
        odds = models.Game.query.get(game).team2_odds
    elif option == 0:
        odds = models.Game.query.get(game).draw_odds
    
    existing_bet = models.Bet.query.filter(models.Bet.user==user).filter(models.Bet.game==game).first()
    if existing_bet:
        existing_bet.option = option
        existing_bet.odds = odds
        db.session.commit()
        return Response(str({'bet_id': existing_bet.id}), status=201)
    else:
        bet = models.Bet(user=user, game=game, option=option, odds=odds)
        db.session.add(bet)
        db.session.commit()
        return Response(str({'bet_id': bet.id}), status=201)

@bp.route('/league/<int:id>', methods=('GET',))
def league(id):
    query = models.League.query.get(id) 
    return jsonify(query.serialize)

@bp.route('/tokens', methods=('GET',))
def tokens():
    query = models.Token.query.all()
    return jsonify([token.serialize for token in query])

@bp.route('/games-by-group/<int:id>', methods=('GET',))
def games_by_group(id):
    query = []
    leagues = models.Group.query.get(id).leagues
    for league in leagues:
        query += league.games
    query.sort(key=lambda item: item.date)
    return jsonify([game.serialize for game in query])

@bp.route('/games-by-user/<int:id>', methods=('GET',))
def games_by_user(id):
    query = []
    memberships = models.User.query.get(id).memberships
    leagues = []
    for membership in memberships:
        leagues += models.Group.query.get(membership.group).leagues
    for league in leagues:
        query += league.games
    query.sort(key=lambda item: item.date)
    return jsonify([game.serialize for game in query])


@bp.route('/bets-by-player-and-group/<int:user_id>/<int:group_id>', methods=('GET',))
def bets_by_player_and_group(user_id, group_id):
    query = models.Bet.query.filter(models.Bet.user==user_id) \
                             .join(models.User, models.User.id==models.Bet.user) \
                             .join(models.Game, models.Game.id==models.Bet.game) \
                             .all()
    games = []
    leagues = models.Group.query.get(group_id).leagues
    for league in leagues:
        games += league.games
    games = [game.id for game in games]
    query = [q for q in query if q.game in games]
    return jsonify([bet.serialize for bet in query])

@bp.route('/bets-by-player/<int:user_id>', methods=('GET',))
def bets_by_player(user_id):
    query = models.Bet.query.filter(models.Bet.user==user_id) \
                             .join(models.User, models.User.id==models.Bet.user) \
                             .join(models.Game, models.Game.id==models.Bet.game) \
                             .all()
    return jsonify([bet.serialize for bet in query])

@bp.route('/login', methods=('POST', ))
def login():
    try:
        request_data = request.get_json()
    except:
        print("coś nie halo")
    print(request_data)
    username = request_data['username']
    password = request_data['password']
    user = models.User.query.filter(models.User.login==username).first()
    if not user:
        return Response(str({'error': 'Invalid username or password'}), status=404)
    
    if user.password != password:
        return Response(str({'error': 'Invalid password'}), status=404)
    token = models.Token(user=user.id, code=models.generate_code(),
                         expiration=datetime.datetime.now() + datetime.timedelta(seconds=30))
    db.session.add(token)
    db.session.commit()
    return Response(str({'token': token.code,
                         'expiration': str(token.expiration),
                         'user_id': user.id,
                         'username': user.login,
                         }), status=201)


@bp.route('/register', methods=('POST', ))
def register():
    request_data = request.get_json()
    username = request_data['username']
    password = request_data['password']
    if models.User.query.filter(models.User.login==username).first():
        return Response(str({'created': False}), status=200)
    user = models.User(login=username, password=password)
    db.session.add(user)
    db.session.commit()
    return Response(str({'Username': user.login, 'created': True}), status=201)


@bp.route('/create-group', methods=('POST', ))
def create_group():
    request_data = request.get_json()
    user = request_data['user']
    name = request_data['name']
    leagues = request_data['leagues']
    print(type(leagues))
    code = models.generate_code()
    user_inst = models.User.query.get(user)
    if not user_inst:
        return Response(str({'created': False}), status=401)
    
    group = models.Group(name=name, code=code)
    db.session.add(group)
    db.session.commit()
    for league in leagues:
        group.leagues.append(models.League.query.get(league))
    membership = models.Membership(user=user_inst.id, group=group.id)
    db.session.add(membership)
    db.session.commit()
    return Response(str({'name': name, 'code': code, 'id': group.id}), status=201)


@bp.route('/join-group', methods=('POST', ))
def join_group():
    request_data = request.get_json()
    user = request_data['user']
    code = request_data['code']
    user_inst = models.User.query.get(user)
    if not user_inst:
        return Response(str({'error': 'User does not exist'}), status=401)
    
    group = models.Group.query.filter(models.Group.code==code).first()
    if not group:
        return Response(str({'error': 'Invalid code'}), status=400)
    
    if models.Membership.query.filter(models.Membership.user==user) \
                              .filter(models.Membership.group==group.id).first():
        return Response(str({'error': 'Already in group'}), status=400)

    membership = models.Membership(user=user_inst.id, group=group.id)
    db.session.add(membership)
    db.session.commit()
    return Response(str({'name': group.name,'code': code, 'id': group.id}), status=200)


@bp.route('/leave-group', methods=('POST', ))
def leave_group():
    request_data = request.get_json()
    user = request_data['user']
    group = request_data['group']
    user_inst = models.User.query.get(user)
    if not user_inst:
        return Response(str({'error': 'User does not exist'}), status=401)
    
    group_inst = models.Group.query.get(group)
    if not group_inst:
        return Response(str({'error': 'Invalid group id'}), status=400)

    membership = models.Membership.query.filter(models.Membership.user==user_inst.id) \
                                        .filter(models.Membership.group==group_inst.id).first()
    
    db.session.delete(membership)
    db.session.commit()
    return Response(str({'name': group_inst.name,'code': group_inst.code, 'id': group_inst.id}), status=200)
