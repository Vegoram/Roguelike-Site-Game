import flask
from flask import jsonify, request
from . import db_session
from data.models.enemy import Enemy


blueprint = flask.Blueprint(
    'enemy_api',
    __name__,
    template_folder='templates'
)

@blueprint.route('/api/enemy')
def get_enemy():
    return "Обработчик в enemy_api"


@blueprint.route('/api/enemy')
def get_news():
    db_sess = db_session.create_session()
    enemy = db_sess.query(Enemy).all()
    return jsonify(
        {
            'enemy':
                [item.to_dict(only=('name', 'location', 'min_level'))
                 for item in enemy]
        }
    )

@blueprint.route('/api/enemy/<int:enemy_api>', methods=['GET'])
def get_one_news(news_id):
    db_sess = db_session.create_session()
    enemy = db_sess.query(Enemy).get(news_id)
    if not enemy:
        return jsonify({'error': 'Not found'})
    return jsonify(
        {
            'enemy': enemy.to_dict(only=(
                'name', 'location', 'min_level'))
        }
    )

@blueprint.route('/api/enemy', methods=['POST'])
def create_news():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['title', 'content', 'user_id', 'is_private']):
        return jsonify({'error': 'Bad request'})
    db_sess = db_session.create_session()
    monster = Enemy(name=request.json['name'],
                    location=request.json['location'],
                    min_level=request.json['min_level'])
    db_sess.add(monster)
    db_sess.commit()
    return jsonify({'success': 'OK'})

@blueprint.route('/api/enemy/<int:enemy_api>', methods=['DELETE'])
def delete_news(news_id):
    db_sess = db_session.create_session()
    enemy = db_sess.query(Enemy).get(news_id)
    if not enemy:
        return jsonify({'error': 'Not found'})
    db_sess.delete(enemy)
    db_sess.commit()
    return jsonify({'success': 'OK'})
