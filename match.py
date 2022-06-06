from flask import Flask, render_template, request, Response, Markup
import json
import pandas as pd
import base64
import io
from io import BytesIO
from mplsoccer.pitch import Pitch
from matplotlib.backends.backend_svg import FigureCanvasSVG



STARTINGXI = {
    "id": 35,
    "name": "Starting XI"
  }

PITCH_LENGTH = 105
PITCH_WIDTH = 69

PITCH_CORRECTIONS = {
            'x': 0,
            'y': 3
        }

LINE_HEIGHTS = {
    'goalkeeper': {
        'home': 4,
        'away': PITCH_LENGTH - 4 - PITCH_CORRECTIONS['x']
    },
    'defense': {
        'home': 12,
        'away': PITCH_LENGTH - 12
    },
    'full-back': {
        'home': 15,
        'away': PITCH_LENGTH - 15
    },
    'defensive_midfield': {
        'home': 22,
        'away': PITCH_LENGTH - 22
    },
    'midfield': {
        'home': 29,
        'away': PITCH_LENGTH - 29
    },
    'attacking_midfield': {
        'home': 36,
        'away': PITCH_LENGTH - 36
    },
    'wing': {
        'home': 41,
        'away': PITCH_LENGTH - 41
    },
    'attack': {
        'home': 47,
        'away': PITCH_LENGTH - 47
    }
}


CORRIDORS = {
    'home': {
        'right': {
            'outer': 8,
            'inner': 16,
            'central': 24,
        },
        'left': {
            'outer': PITCH_WIDTH - 8 - PITCH_CORRECTIONS['y'],
            'inner': PITCH_WIDTH - 16 - PITCH_CORRECTIONS['y'],
            'central': PITCH_WIDTH - 24 - PITCH_CORRECTIONS['y']
        }
    },
    'away': {
        'right': {
            'outer': PITCH_WIDTH - 8 - PITCH_CORRECTIONS['y'],
            'inner': PITCH_WIDTH - 16 - PITCH_CORRECTIONS['y'],
            'central': PITCH_WIDTH - 24 - PITCH_CORRECTIONS['y']
        },
        'left': {
            'outer': 8,
            'inner': 16,
            'central': 24,
        }
    }
}

CENTER = 33

POSITION_CODES = {
    'Goalkeeper': 'gk',
    'Right Back': 'rb',
    'Left Back': 'lb',
    'Right Center Back': 'rcb',
    'Left Center Back': 'lcb',
    'Center Back': 'cb',
    'Right Defensive Midfield': 'rdm',
    'Center Defensive Midfield': 'cdm',
    'Left Defensive Midfield': 'ldm',
    'Right Center Midfield': 'rcm',
    'Left Center Midfield': 'lcm',
    'Center Midfield': 'cm',
    'Right Midfield': 'rm',
    'Left Midfield': 'lm',
    'Center Attacking Midfield': 'cam',
    'Right Wing': 'rw',
    'Left Wing': 'lw',
    'Right Center Forward': 'rcf',
    'Left Center Forward': 'lcf',
    'Center Forward': 'st',
}

class Match:
    def getData(self, match_id):
        global data
        data = pd.read_json(open('data/events/{0}.json'.format(match_id)))
        data = data['tactics'].where(data['type'] == STARTINGXI).dropna(axis=0, how='all')
        return data

    def drawPitch(self):
        pitch = Pitch(pitch_color='grass', line_color='white', stripe=True, pitch_type='uefa', goal_type='box', pitch_length=PITCH_LENGTH,
                      pitch_width=PITCH_WIDTH)
        fig, ax = pitch.draw()

        self.drawFormation(pitch, ax)

        return fig, ax

    def render_img(self, fig):
        buf = io.StringIO()
        fig.savefig(buf, format="svg")

        return Markup(buf.getvalue())

    def getPosition(self, position, side):
        positions = {
            'gk': (LINE_HEIGHTS['goalkeeper'][side], CENTER),

            'rb': (LINE_HEIGHTS['full-back'][side], CORRIDORS[side]['right']['outer']),
            'lb': (LINE_HEIGHTS['full-back'][side], CORRIDORS[side]['left']['outer']),
            'rcb': (LINE_HEIGHTS['defense'][side], CORRIDORS[side]['right']['central']),
            'lcb': (LINE_HEIGHTS['defense'][side], CORRIDORS[side]['left']['central']),
            'cb': (LINE_HEIGHTS['defense'][side], CENTER),

            'rdm': (LINE_HEIGHTS['defensive_midfield'][side], CORRIDORS[side]['right']['central']),
            'ldm': (LINE_HEIGHTS['defensive_midfield'][side], CORRIDORS[side]['left']['central']),
            'cdm': (LINE_HEIGHTS['defensive_midfield'][side], CENTER),

            'rcm': (LINE_HEIGHTS['midfield'][side], CORRIDORS[side]['right']['central']),
            'lcm': (LINE_HEIGHTS['midfield'][side], CORRIDORS[side]['left']['central']),
            'cm': (LINE_HEIGHTS['midfield'][side], CENTER),

            'rm': (LINE_HEIGHTS['attacking_midfield'][side], CORRIDORS[side]['right']['inner']),
            'lm': (LINE_HEIGHTS['attacking_midfield'][side], CORRIDORS[side]['left']['inner']),

            'cam': (LINE_HEIGHTS['attacking_midfield'][side], CENTER),

            'rcf': (LINE_HEIGHTS['attack'][side], CORRIDORS[side]['right']['central']),
            'lcf': (LINE_HEIGHTS['attack'][side], CORRIDORS[side]['left']['central']),

            'rw': (LINE_HEIGHTS['wing'][side], CORRIDORS[side]['right']['outer']),
            'lw': (LINE_HEIGHTS['wing'][side], CORRIDORS[side]['left']['outer']),

            'st': (LINE_HEIGHTS['attack'][side], CENTER),
        }

        return positions[position]

    def draw_player(self, number, position, home, pitch, ax):

        if home:
            kit_color = 'blue'
            side = 'home'
        else:
            kit_color = 'red'
            side = 'away'

        font_size = 12

        padding = 0.5 if number < 10 else 0.4

        pitch.annotate(number, self.getPosition(position, side),
                       color='white',
                       bbox=dict(fc=kit_color, alpha=0.7, boxstyle='circle', pad=padding),
                       ha='center',
                       fontsize=font_size, ax=ax)

    def drawFormation(self, pitch, ax):

        global data
        index = 0

        for team in data:
            for player in team['lineup']:
                jersey_number = player['jersey_number']
                position = POSITION_CODES[player['position']['name']]
                home = True if index == 0 else False

                self.draw_player(jersey_number, position, home, pitch, ax)

            index = index + 1

        """
        self.draw_player(1, 'gk', True, pitch, ax)
        self.draw_player(2, 'rb', True, pitch, ax)
        self.draw_player(4, 'rcb', True, pitch, ax)
        self.draw_player(5, 'lcb', True, pitch, ax)
        self.draw_player(3, 'lb', True, pitch, ax)
        self.draw_player(6, 'rdm', True, pitch, ax)
        self.draw_player(8, 'ldm', True, pitch, ax)
        self.draw_player(10, 'rm', True, pitch, ax)
        self.draw_player(11, 'lm', True, pitch, ax)
        self.draw_player(7, 'rcf', True, pitch, ax)
        self.draw_player(9, 'lcf', True, pitch, ax)

        self.draw_player(1, 'gk', False, pitch, ax)
        self.draw_player(2, 'rb', False, pitch, ax)
        self.draw_player(4, 'rcb', False, pitch, ax)
        self.draw_player(5, 'lcb', False, pitch, ax)
        self.draw_player(3, 'lb', False, pitch, ax)
        self.draw_player(6, 'rcm', False, pitch, ax)
        self.draw_player(8, 'lcm', False, pitch, ax)
        self.draw_player(10, 'cam', False, pitch, ax)
        self.draw_player(11, 'lw', False, pitch, ax)
        self.draw_player(7, 'rw', False, pitch, ax)
        self.draw_player(9, 'st', False, pitch, ax)
        """

