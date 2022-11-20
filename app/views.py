from flask import (
    Blueprint, jsonify
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


@bp.route('/users', methods=('GET', 'POST'))
def users():
    query = models.User.query.all()
    return jsonify([user.serialize for user in query])


@bp.route('/leagues', methods=('GET', 'POST'))
def leagues():
    query = models.League.query.all()
    return jsonify([league.serialize for league in query])


@bp.route('/games', methods=('GET', 'POST'))
def games():
    query = models.Game.query.all()
    return jsonify([game.serialize for game in query])


@bp.route('/group/<int:id>', methods=('GET', 'POST'))
def group(id):
    query = models.Group.query.get(id)
    return jsonify(query.serialize)

@bp.route('/games-by-league/<int:id>', methods=('GET', 'POST'))
def league(id):
    query = models.League.query.get(id).games
    return jsonify([game.serialize for game in query])

@bp.route('/groups-by-user/<int:id>', methods=('GET', 'POST'))
def group_by_user(id):
    query = models.User.query.get(id).memberships
    return jsonify([group.serialize for group in query])


@bp.route('/user/<int:id>', methods=('GET', 'POST'))
def user(id):
    query = models.User.query.get(id)
    return jsonify(query.serialize)


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
        leagues += membership.leagues
    for league in leagues:
        query += league.games
    query.sort(key=lambda item: item.date)
    return jsonify([game.serialize for game in query])
