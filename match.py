from flask import Markup
import pandas as pd
import io

from lineup import Lineup

STARTINGXI = {
    "id": 35,
    "name": "Starting XI"
  }

class Match:
    def __init__(self, match_id):
        self.d = pd.read_json(open('data/events/{0}.json'.format(match_id)))

    def getLineup(self):
        data = self.d['tactics'].where(self.d['type'] == STARTINGXI).dropna(axis=0, how='all')
        return data

    def drawLineup(self):
        lineup = Lineup(self.getLineup())

        fig, ax = lineup.drawPitch()

        return fig, ax



    def render_img(self, fig):
        buf = io.StringIO()
        fig.savefig(buf, format="svg")

        return Markup(buf.getvalue())

