from flask import Flask, render_template
from data import db_session
from werkzeug.utils import redirect
from data.models.player import Player
from data.forms import *
from flask_login import LoginManager, login_user, login_required, logout_user


db_session.global_init('db/game_database.db')
app = Flask(__name__)
app.config['SECRET_KEY'] = '3yzwyB8X88GaxcWDLkmFXG05GC0brVLKCTJFtr1'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(player_id):
    db_sess = db_session.create_session()
    return db_sess.query(Player).get(player_id)


@app.route('/')
def main_page():
    return render_template('basic_template.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = NewPlayerForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('registration_page.html', heading='Регистрация',
                                   form=form,
                                   message='Пароли не совпадают')
        db_sess = db_session.create_session()
        if db_sess.query(Player).filter(Player.email == form.email.data).first():
            return render_template('registration_page.html', heading='Регистрация',
                                   form=form,
                                   message='Пользователь с такой почтой уже есть')
        if form.player_class.data == 1:
            health = 40
        else:
            health = 30
        player = Player(
            email=form.email.data,
            name=form.name.data,
            surname=form.surname.data,
            nickname=form.nickname.data,
            inventory=None,
            equipped=None,
            money=0,
            location='square/0/free',
            player_class=form.player_class.data,
            hp=health,
            level=1)
        player.set_password(form.password.data)
        db_sess.add(player)
        db_sess.commit()
        return redirect('/')
    return render_template('registration_page.html', heading='Регистрация', form=form)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
