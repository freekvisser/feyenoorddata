from flask import Flask, render_template, request, Response, Markup
import json
import pandas as pd
import base64
import io
from io import BytesIO
from mplsoccer.pitch import Pitch
from matplotlib.backends.backend_svg import FigureCanvasSVG
from matplotlib import font_manager

font_dirs = ['static/assets/fonts/ampero/ttf']
font_files = font_manager.findSystemFonts(fontpaths=font_dirs)

for font_file in font_files:
    font_manager.fontManager.addfont(font_file)




PITCH_LENGTH = 105
PITCH_WIDTH = 69

PITCH_CORRECTIONS = {
            'x': -0,
            'y': 3
        }

LINE_HEIGHTS = {
    'goalkeeper': {
        'home': 4,
        'away': PITCH_LENGTH - 4 - PITCH_CORRECTIONS['x']
    },
    'defense': {
        'home': 12,
        'away': PITCH_LENGTH - 12 - PITCH_CORRECTIONS['x']
    },
    'full-back': {
        'home': 15,
        'away': PITCH_LENGTH - 15 - PITCH_CORRECTIONS['x']
    },
    'defensive_midfield': {
        'home': 22,
        'away': PITCH_LENGTH - 22 - PITCH_CORRECTIONS['x']
    },
    'midfield': {
        'home': 29,
        'away': PITCH_LENGTH - 29 - PITCH_CORRECTIONS['x']
    },
    'attacking_midfield': {
        'home': 36,
        'away': PITCH_LENGTH - 36 - PITCH_CORRECTIONS['x']
    },
    'wing': {
        'home': 41,
        'away': PITCH_LENGTH - 41 - PITCH_CORRECTIONS['x']
    },
    'attack': {
        'home': 47,
        'away': PITCH_LENGTH - 47 - PITCH_CORRECTIONS['x']
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

STARTINGXI = {
    "id": 35,
    "name": "Starting XI"
  }

class Lineup:

    def __init__(self, lineup, substitutions):
        self.d = lineup
        self.substitutions = substitutions


    def drawPitch(self):
        pitch = Pitch(pitch_color='grass', line_color='white', stripe=True, pitch_type='uefa', goal_type='box', pitch_length=PITCH_LENGTH,
                      pitch_width=PITCH_WIDTH)
        fig, ax = pitch.draw()



        self.drawFormation(pitch, ax)

        return fig, ax

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

    def draw_player(self, number, position, home, subbed, pitch, ax):

        if home:
            kit_color = 'blue'
            side = 'home'
            arrow = 'larrow'
        else:
            kit_color = 'red'
            side = 'away'
            arrow = 'rarrow'

        if subbed:
            boxStyle = arrow
        else:
            boxStyle = 'circle'

        font_size = 13

        padding = 0.5 if number < 10 else 0.45

        pitch.annotate(number, self.getPosition(position, side),
                       color='white',
                       bbox=dict(fc=kit_color, alpha=0.7, boxstyle=boxStyle, pad=padding),
                       ha='center',
                       fontname='Ampero',

                       fontsize=font_size, ax=ax)

    def getSubbedOffPlayers(self, side):
        if side:
            substitutions = self.substitutions['home']
        else:
            substitutions = self.substitutions['away']

        subbedOffPlayers = []

        for substitution in substitutions:
            subbedOffPlayers.append(substitution['replaced']['id'])


        return subbedOffPlayers

    def drawFormation(self, pitch, ax):

        data = self.d
        index = 0


        for team in data:
            for player in team['lineup']:

                jersey_number = player['jersey_number']
                position = POSITION_CODES[player['position']['name']]
                home = True if index == 0 else False

                subbedOffPlayers = self.getSubbedOffPlayers(home)

                subbed = False
                player_id = player['player']['id']
                if player_id in subbedOffPlayers:
                    subbed = True

                self.draw_player(jersey_number, position, home, subbed, pitch, ax)

            index = index + 1
