from flask import Markup
import pandas as pd
import io
import math


from lineup import Lineup
from shots import Shots

STARTINGXI = {
    "id": 35,
    "name": "Starting XI"
}

SUBSTITUTION = {
    "id": 19,
    "name": "Substitution"
}

SHOT = {
    "id": 16,
    "name": "Shot"
}

OWN_GOAL_FOR = {
    "id" : 25,
    "name" : "Own Goal For"
}
OWN_GOAL_AGAINST = {
    "id" : 20,
    "name" : "Own Goal Against"
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

    def getSubstitutions(self):
        data = self.d[(self.d['type'] == SUBSTITUTION)].dropna(axis=1, how='any')
        return data

    def getShots(self, side):
        data = self.d[(self.d['type'] == SHOT) & (self.d['team'] == side)].dropna(axis=1, how='any')
        own_goals = pd.concat([self.d[(self.d['type'] == OWN_GOAL_FOR) & (self.d['team'] == side)].dropna(axis=1, how='any'), self.d[(self.d['type'] == OWN_GOAL_AGAINST) & (self.d['team'] == side)].dropna(axis=1, how='any')])

        return pd.concat([data, own_goals])

    def drawLineup(self):
        lineup = Lineup(self.getLineup(), self.getSubstitutions())

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

    def getPossession(self, side):
        sides = self.getHomeAndAway()
        team = sides[0] if side else sides[1]
        possession = self.d[(self.d['team'] == team)]['duration'].values
        totalSeconds = self.d['duration'].values
        totalPossessionInSeconds = 0
        possessionInSeconds = 0
        for seconds in totalSeconds:
            if not math.isnan(seconds):
                totalPossessionInSeconds += seconds
        for seconds in possession:
            if not math.isnan(seconds):
                possessionInSeconds += seconds

        return round(possessionInSeconds / totalPossessionInSeconds * 100)
