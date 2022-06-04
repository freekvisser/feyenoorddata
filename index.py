from flask import Flask, render_template, request
import json
import pandas as pd

app = Flask(__name__)

app.secret_key = 'SOME_SECRET_KEY'

startingXI = {
    "id" : 35,
    "name" : "Starting XI"
  }

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
    matchID = request.args.get('match')
    with open('data/events/{0}.json'.format(matchID)) as json_file:
        item = json.load(json_file)

    pandas_json = pd.read_json(open('data/events/{0}.json'.format(matchID)))
    pandas_json = pandas_json['tactics'].where(pandas_json['type'] == startingXI).dropna(axis=0, how='all')
    return render_template('match.html', match=[], pandas=pandas_json.values)


@app.route('/test')
def background_process_test():
    player = flask.request.args.get('player')
    flask.session['player'] = player
    return flask.jsonify({"response": player})


app.run(host='0.0.0.0', port=8000, debug=True)