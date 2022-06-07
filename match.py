from flask import Markup
import pandas as pd
import io

from lineup import Lineup
from shots import Shots

STARTINGXI = {
    "id": 35,
    "name": "Starting XI"
}

SHOT = {
    "id": 16,
    "name": "Shot"
}


def render_img(fig):
    buf = io.StringIO()
    fig.savefig(buf, format="svg")

    return Markup(buf.getvalue())


class Match:
    def __init__(self, match_id):
        self.d = pd.read_json(open('data/events/{0}.json'.format(match_id)))

    def getHomeAndAway(self):
        data = self.d[(self.d['type'] == STARTINGXI)].dropna(axis=0, how='all')
        home = data['team'][0]
        away = data['team'][1]
        return [home, away]

    def getLineup(self):
        data = self.d['tactics'].where(self.d['type'] == STARTINGXI).dropna(axis=0, how='all')
        return data

    def getShots(self, side):
        data = self.d[(self.d['type'] == SHOT) & (self.d['team'] == side)].dropna(axis=1, how='any')
        return data

    def drawLineup(self):
        lineup = Lineup(self.getLineup())

        fig, ax = lineup.drawPitch()

        return render_img(fig)

    def drawShots(self, side):
        sides = self.getHomeAndAway()
        team = sides[0] if side else sides[1]
        teamName = team['name']

        shots = Shots(self.getShots(team))

        fig, ax = shots.drawPitch()

        statisticsData = shots.getStatistics()

        statisticsData['name'] = teamName
        statisticsData['plot'] = render_img(fig)

        return statisticsData
