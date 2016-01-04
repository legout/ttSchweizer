#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import os
import re
from datetime import datetime
from urllib.parse import quote_plus

import flask
from flask import Flask, request, session, render_template, flash
from flask.ext.login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask.ext.sqlalchemy import SQLAlchemy

import ttSchweizer
from ttSchweizer import Turnier, Spieler_Collection, getFileNameOfRound


def message(s, category='none'):
    if 'Noch kein Ergebnis für' in s:
        return

    # runde-1.txt --> Runde 1
    s = re.sub('runde-(\d+).txt', lambda m: 'Runde ' + m.group(1), s)
    flash(s, category)


ttSchweizer.message = message

app = Flask(__name__)
app.debug = True
app.secret_key = 'F1r4o6doM%imi!/Baum'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sql.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = '/login'
login_manager.login_message = 'Bitte einloggen'
login_manager.login_message_category = 'info'
login_manager.needs_refresh_message_category = 'info'

db = SQLAlchemy(app)


def getUserDirector():
    return os.path.join(STARTcURRENTwORKINGdIR, current_user.username)

def changeToUserDirectory():
    os.chdir(getUserDirector())
    
def changeToTurnierDirectory(directory):
    changeToUserDirectory()
    os.chdir(directory)


def getExistingTurniere():
    return sorted([entry for entry in os.listdir(getUserDirector()) if os.path.isdir(entry)])


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    password = db.Column(db.String)


@login_manager.user_loader
def user_loader(user_id):
    user = User.query.filter_by(id=user_id)
    if user.count() == 1:
        return user.one()
    return None


@app.before_first_request
def init_request():
    db.create_all()


@app.route('/logout')
def logout():
    logout_user()
    return flask.redirect(flask.url_for('main'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('User/register.html')
    elif request.method == 'POST':
        username = request.form['txtUsername']
        password = request.form['txtPassword']

        user = User.query.filter_by(username=username)
        if user.count() == 0:
            user = User(username=username, password=password)
            db.session.add(user)
            db.session.commit()

            flash('Der Username {0} wurde registriert. Bitte einloggen'.format(username))
            return flask.redirect(flask.url_for('login'))
        else:
            flash('Der Username {0} ist schon vergeben.  Bitte einen anderen probieren.'.format(username))
            return flask.redirect(flask.url_for('register'))
    else:
        flask.abort(405)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('User/login.html', next=request.args.get('next'))
    elif request.method == 'POST':
        username = request.form['txtUsername']
        password = request.form['txtPassword']

        user = User.query.filter_by(username=username).filter_by(password=password)
        if user.count() == 1:
            login_user(user.one())

            if not os.path.exists(getUserDirector()):
                os.makedirs(getUserDirector())

            flash('Servus {0}'.format(username))
            try:
                next = request.form['next']
                return flask.redirect(next)
            except:
                return flask.redirect(flask.url_for('main'))
        else:
            flash('Ungültiger Login')
            return flask.redirect(flask.url_for('login'))
    else:
        return flask.abort(405)


@app.route("/")
@login_required
def main():
    changeToUserDirectory()
    if 'turnierName' not in session or not os.path.exists(session['turnierName']):
        return flask.redirect(flask.url_for('new'))

    changeToTurnierDirectory(session['turnierName'])

    turnier = Turnier()
    spieler = turnier.getSpieler()
    ranking = spieler.getRanking()
    rankedSpieler = [sub[0] for sub in ranking]

    currentRound = turnier.getLastRound()

    begegnungen = '!'.join(currentRound.getUnfinishedBegegnungenFlat())

    currentRoundNumber = currentRound.getNumberOfRound()
    if 'expertMode' in session and session['expertMode'] or currentRoundNumber <= 0:
        textToEdit = Turnier.getDefiningTextFor(currentRoundNumber)
    else:
        textToEdit = False

    return render_template('ranking.html', ranking=ranking, runde=currentRoundNumber,
                           auslosen=currentRound.isComplete(),
                           thereAreFreilose=spieler.freiloseNeeded(),
                           spielerList=rankedSpieler,
                           begegnungen=begegnungen, text=textToEdit)


@app.route("/auslosen")
@login_required
def auslosen():
    changeToTurnierDirectory(session['turnierName'])
    turnier = Turnier()
    turnier.auslosen()
    return flask.redirect(flask.url_for('main'))


@app.route("/spielerZettel/<int:runde>/<begegnungen>")
@login_required
def spielerZettel(runde, begegnungen):
    from flask_weasyprint import HTML, render_pdf

    l = begegnungen.split('!')

    now = datetime.now().strftime("%d.%m.%Y")
    html = render_template('spieler_zettel.html', begegnungen=zip(l[0::2], l[1::2]),
                           runde=runde, date=now)
    return render_pdf(HTML(string=html), download_filename='begegnungen_runde{}.pdf'.format(runde))
    #return html


@app.route("/new", methods=['GET', 'POST'])
@login_required
def new():
    error = None

    changeToUserDirectory()

    if request.method == 'POST':
        turnierName = quote_plus(request.form['turniername'])
        if os.path.exists(turnierName):
            error = "Ein Turnier mit dem Namen {} existiert schon".format(turnierName)
        else:
            os.mkdir(turnierName, 0o755)
            os.chdir(turnierName)
            flask.get_flashed_messages()
            session['turnierName'] = turnierName
            session['exportMode'] = False
            flash('{} wurde gestartet'.format(turnierName), 'info')
            return flask.redirect(flask.url_for('main'))

    return render_template('new.html', error=error, existingTurniere=getExistingTurniere())


@app.route("/edit/<int:roundNumber>", methods=['GET', 'POST'])
@login_required
def edit(roundNumber):
    changeToTurnierDirectory(session['turnierName'])
    error = None
    definingFileForRound = getFileNameOfRound(roundNumber)
    if not os.path.exists(definingFileForRound):
        flash("Die Runde {} kann nicht editiert werden!".format(roundNumber), 'info')
        return flask.redirect(flask.url_for('main'))

    if request.method == 'POST':
        if request.form['action'] == 'Löschen':
            os.remove(definingFileForRound)
        else:
            textToWrite = request.form['text']
            with open(definingFileForRound, "w", encoding='utf-8') as roundFile:
                roundFile.write(textToWrite)

        return flask.redirect(flask.url_for('main'))

    return render_template('edit.html', error=error, runde=roundNumber,
                           text=Turnier.getDefiningTextFor(roundNumber))


@app.route("/editSingle/<int:roundNumber>/<a>/<b>", methods=['POST'])
@login_required
def editSingle(roundNumber, a, b):
    changeToTurnierDirectory(session['turnierName'])
    result = '{}:{}  {} {} {} {} {}'.format(request.form['setWon'], request.form['setLost'],
                                            request.form['set1'], request.form['set2'], request.form['set3'],
                                            request.form['set4'], request.form['set5'])
    result = result.strip(' :')
    definingFileForRound = getFileNameOfRound(roundNumber)
    wholeRoundDef = Turnier.getDefiningTextFor(roundNumber)
    # Vertausche Spieler
    aMatchResult = ttSchweizer.parseMatchResult(result, '{} <> {}'.format(a,b), result, roundNumber)
    if aMatchResult:
        mt = aMatchResult.turned()
        resultTurned = '{}:{} '.format(mt.gamesWonByPlayerA, mt.gamesWonByPlayerB)
        resultTurned += ' '.join(mt.gamePoints)
    else:
        return flask.redirect(flask.url_for('main'))

    for p1, p2, res in ((a,b,result),(b,a,resultTurned)):
        wholeRoundDef = re.sub('{a}\s*<>\s*{b}\s*!.*'.format(a=p1, b=p2),
                           '{} <> {} ! {}'.format(p1, p2, res),
                           wholeRoundDef)

    with open(definingFileForRound, "w", encoding='utf-8') as roundFile:
        roundFile.write(wholeRoundDef)

    return flask.redirect(flask.url_for('main'))



@app.route("/setTurnier/<turnier>")
@login_required
def setTurnier(turnier):
    session['turnierName'] = turnier
    session['exportMode'] = False
    changeToTurnierDirectory(session['turnierName'])
    return flask.redirect(flask.url_for('main'))


@app.route('/expertMode/<int:mode>')
@login_required
def expertMode(mode):
    session['expertMode'] = (mode != 0)
    return flask.redirect(flask.url_for('main'))


@app.route('/favicon.ico')
def favicon():
    return flask.send_from_directory(os.path.join(app.root_path, 'static'),
                                     'favicon.ico', mimetype='image/vnd.microsoft.icon')


if __name__ == "flask_app":
    os.chdir('ttSchweizerData')
    STARTcURRENTwORKINGdIR = os.getcwd()

if __name__ == "__main__":
    STARTcURRENTwORKINGdIR = os.getcwd()
    app.run()
