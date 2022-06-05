from flask import Flask, render_template, request
import json
import pandas as pd
import base64
from io import BytesIO
from mplsoccer.pitch import Pitch


STARTINGXI = {
    "id": 35,
    "name": "Starting XI"
  }

PITCH_LENGTH = 105
PITCH_WIDTH = 69

pitch_corrections = {
            'x': 0,
            'y': 3
        }

LINE_HEIGHTS = {
    'defense': {
        'home': 10,
        'away': PITCH_LENGTH - 10 - pitch_corrections['x']
    },
    'full-back': {
        'home': 15,
        'away': PITCH_LENGTH - 15 - pitch_corrections['x']
    },
    'defensive_midfield': {
        'home': 22,
        'away': PITCH_LENGTH - 22 - pitch_corrections['x']
    },
    'midfield': {
        'home': 29,
        'away': PITCH_LENGTH - 29 - pitch_corrections['x']
    },
    'attacking_midfield': {
        'home': 36,
        'away': PITCH_LENGTH - 36 - pitch_corrections['x']
    },
    'wing': {
        'home': 41,
        'away': PITCH_LENGTH - 41 - pitch_corrections['x']
    },
    'attack': {
        'home': 47,
        'away': PITCH_LENGTH - 47 - pitch_corrections['x'] - 3
    }
}

CORRIDORS = {
    'outer': 8,
    'inner': 16,
    'central': 24
}

CENTER = 33

POSITION_CODES = {
    'Goalkeeper': 'gk',
    'Right Back': 'rb',
    'Left Back': 'lb',
    'Right Center Back': 'rcb',
    'Left Center Back': 'lcb',
    'Right Defensive Midfield': 'rdm',
    'Center Defensive Midfield': 'cdm',
    'Left Defensive Midfield': 'ldm',
    'Right Center Midfield': 'rcm',
    'Left Center Midfield': 'lcm',
    'Center Midfield': 'cm',
    'Right Midfield': 'rm',
    'Left Midfield': 'lm',
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
        pitch = Pitch(pitch_color='grass', line_color='white', stripe=True, pitch_type='uefa', pitch_length=PITCH_LENGTH,
                      pitch_width=PITCH_WIDTH)
        fig, ax = pitch.draw()

        self.drawFormation(pitch, ax)

        return fig, ax

    def render_img(self, fig):
        buf = BytesIO()
        fig.savefig(buf, format="png")
        return base64.b64encode(buf.getbuffer()).decode("ascii")

    def draw442(self):
        print(442)



    def draw_player(self, number, position, home, pitch, ax):
        formations = [data[0]['formation'], data[1]['formation']]

        formationSwitch = {442: self.draw442,
                           }

        home_positions = {
            'gk': (0, CENTER),

            'rb': (LINE_HEIGHTS['full-back']['home'], CORRIDORS['outer']),
            'lb': (LINE_HEIGHTS['full-back']['home'], PITCH_WIDTH - CORRIDORS['outer'] - pitch_corrections['y']),
            'rcb': (LINE_HEIGHTS['defense']['home'], CORRIDORS['central']),
            'lcb': (LINE_HEIGHTS['defense']['home'], PITCH_WIDTH - CORRIDORS['central'] - pitch_corrections['y']),

            'rdm': (LINE_HEIGHTS['defensive_midfield']['home'], CORRIDORS['central']),
            'ldm': (LINE_HEIGHTS['defensive_midfield']['home'], PITCH_WIDTH - CORRIDORS['central'] - pitch_corrections['y']),
            'cdm': (LINE_HEIGHTS['defensive_midfield']['home'], CENTER),

            'rcm': (LINE_HEIGHTS['midfield']['home'], CORRIDORS['central']),
            'lcm': (LINE_HEIGHTS['midfield']['home'], PITCH_WIDTH - CORRIDORS['central'] - pitch_corrections['y']),
            'cm': (LINE_HEIGHTS['midfield']['home'], CENTER),

            'rm': (LINE_HEIGHTS['attacking_midfield']['home'], CORRIDORS['inner']),
            'lm': (LINE_HEIGHTS['attacking_midfield']['home'], PITCH_WIDTH - CORRIDORS['inner'] - pitch_corrections['y']),

            'cam': (LINE_HEIGHTS['attacking_midfield']['home'], CENTER),

            'rcf': (LINE_HEIGHTS['attack']['home'], CORRIDORS['central']),
            'lcf': (LINE_HEIGHTS['attack']['home'], PITCH_WIDTH - CORRIDORS['central'] - pitch_corrections['y']),

            'rw': (LINE_HEIGHTS['wing']['home'], CORRIDORS['outer']),
            'lw': (LINE_HEIGHTS['wing']['home'], PITCH_WIDTH - CORRIDORS['outer'] - pitch_corrections['y']),

            'st': (LINE_HEIGHTS['attack']['home'], CENTER),
        }
        away_positions = {
            'gk': (PITCH_LENGTH - 0 - pitch_corrections['x'], CENTER),

            'lb': (LINE_HEIGHTS['full-back']['away'], CORRIDORS['outer']),
            'rb': (LINE_HEIGHTS['full-back']['away'], PITCH_WIDTH - CORRIDORS['outer'] - pitch_corrections['y']),
            'lcb': (LINE_HEIGHTS['defense']['away'], CORRIDORS['central']),
            'rcb': (LINE_HEIGHTS['defense']['away'], PITCH_WIDTH - CORRIDORS['central'] - pitch_corrections['y']),

            'ldm': (LINE_HEIGHTS['defensive_midfield']['away'], CORRIDORS['central']),
            'rdm': (LINE_HEIGHTS['defensive_midfield']['away'], PITCH_WIDTH - CORRIDORS['central'] - pitch_corrections['y']),
            'cdm': (LINE_HEIGHTS['defensive_midfield']['away'], CENTER),

            'lcm': (LINE_HEIGHTS['midfield']['away'], CORRIDORS['central']),
            'rcm': (LINE_HEIGHTS['midfield']['away'], PITCH_WIDTH - CORRIDORS['central'] - pitch_corrections['y']),
            'cm': (LINE_HEIGHTS['midfield']['away'], CENTER),

            'lm': (LINE_HEIGHTS['attacking_midfield']['away'], CORRIDORS['inner']),
            'rm': (LINE_HEIGHTS['attacking_midfield']['away'], PITCH_WIDTH - CORRIDORS['inner'] - pitch_corrections['y']),

            'cam': (LINE_HEIGHTS['attacking_midfield']['away'], CENTER),

            'lcf': (LINE_HEIGHTS['attack']['away'], CORRIDORS['central']),
            'rcf': (LINE_HEIGHTS['attack']['away'], PITCH_WIDTH - CORRIDORS['central'] - pitch_corrections['y']),

            'lw': (LINE_HEIGHTS['wing']['away'], CORRIDORS['outer']),
            'rw': (LINE_HEIGHTS['wing']['away'], PITCH_WIDTH - CORRIDORS['outer'] - pitch_corrections['y']),

            'st': (LINE_HEIGHTS['attack']['away'], CENTER),
        }

        kit_color = 'blue' if home == True else 'red'

        positions = home_positions if home == True else away_positions

        font_size = 12

        padding = 0.5 if number < 10 else 0.4

        pitch.annotate(number, positions[position],
                       color='white',
                       bbox=dict(fc=kit_color, alpha=0.5, boxstyle='circle', pad=padding),
                       fontsize=font_size, ax=ax)

    def drawFormation(self, pitch, ax):

        global data
        index = 0

        for team in data:
            for player in team['lineup']:
                jersey_number = player['jersey_number']
                position = POSITION_CODES[player['position']['name']]
                home = True if index == 0 else False

                print(player['player']['name'])


                self.draw_player(jersey_number, position, home, pitch, ax)

            index = index + 1


        formations = [data[0]['formation'], data[1]['formation']]

        formationSwitch = {442: self.draw442,
                   }
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

