from flask import Flask, render_template, request
import json

app = Flask(__name__)

with open('data/competitions.json') as json_file:
    data = json.load(json_file)


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


app.run(host='0.0.0.0', port=8000, debug=True)