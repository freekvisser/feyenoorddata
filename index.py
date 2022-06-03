from flask import Flask, render_template, request
import json

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


@app.route('/match')
def match():
    competition = request.args.get('competition')
    season = request.args.get('season')
    with open('data/matches/{0}/{1}.json'.format(competition, season)) as json_file:
        games = json.load(json_file)
    return render_template('match.html', games=games)


@app.route('/test')
def background_process_test():
    player = flask.request.args.get('player')
    flask.session['player'] = player
    return flask.jsonify({"response": player})


app.run(host='0.0.0.0', port=8000, debug=True)