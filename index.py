from flask import Flask, render_template, request, Markup
import json
import pandas as pd
import base64
from io import BytesIO
from mplsoccer.pitch import Pitch
from match import Match


app = Flask(__name__)

app.secret_key = 'SOME_SECRET_KEY'

with open('data/competitions.json') as json_file:
    data = json.load(json_file)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/competitions')
def competitions():
    return render_template('competitions.html', competitions=data)


@app.route('/matches')
def matches():
    competitionID = request.args.get('competition')
    seasonID = request.args.get('season')
    with open('data/matches/{0}/{1}.json'.format(competitionID, seasonID)) as json_file:
        items = json.load(json_file)
    return render_template('matches.html', matches=items)

@app.route('/match')
def match():
    match_id = request.args.get('match')
    match = Match(match_id)

    match_data = match.getLineup()

    lineup = match.drawLineup()
    home_shots = match.drawShots(True)
    away_shots = match.drawShots(False)

    return render_template('match.html', matchData=match_data.values, lineup=lineup, home_shots=home_shots, away_shots=away_shots)


@app.route('/test')
def background_process_test():
    player = flask.request.args.get('player')
    flask.session['player'] = player
    return flask.jsonify({"response": player})


app.run(host='0.0.0.0', port=8000, debug=True)