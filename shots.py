from mplsoccer.pitch import VerticalPitch, Pitch
from datetime import datetime,date
import pandas as pd



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


class Shots:
    def __init__(self, data):
        self.d = data
        self.shots = self.d[(self.d['type'] == SHOT)]
        self.own_goals = {
            'for': self.d[(self.d['type'] == OWN_GOAL_FOR)],
            'against': self.d[(self.d['type'] == OWN_GOAL_AGAINST)]
        }

    def drawPitch(self):
        data = self.shots
        pitch = VerticalPitch(half=True, goal_type='box')
        fig, ax = pitch.draw()

        shots = []
        offTarget = []
        blocked = []
        post = []
        onTarget = []
        goals = []

        for index, row in data.iterrows():
            shot = row['shot']
            xG = shot['statsbomb_xg']
            location = row['location']
            end_location = shot['end_location']
            data = {
                'xG': xG,
                'location': location,
                'end_location': end_location,
            }

            if shot['outcome']['name'] == 'Goal':
                goals.append(data)
            elif shot['outcome']['name'] == 'Saved':
                onTarget.append(data)
            elif shot['outcome']['name'] == 'Blocked':
                blocked.append(data)
            elif shot['outcome']['name'] == 'Off T' or shot['outcome']['name'] == 'Wayward':
                offTarget.append(data)
            elif shot['outcome']['name'] == 'Post':
                post.append(data)
            else:
                shots.append(data)

        for shot in shots:
            pitch.scatter(shot['location'][0], shot['location'][1], s=(shot['xG'] * 900) + 100, marker='^',
                          edgecolors='black', c='#ff0000', alpha=0.7, ax=ax)
            pitch.arrows(shot['location'][0], shot['location'][1], shot['end_location'][0], shot['end_location'][1],
                         ax=ax)
        for shot in offTarget:
            pitch.scatter(shot['location'][0], shot['location'][1], s=(shot['xG'] * 900) + 100, marker='^',
                          edgecolors='black', c='#FF0000', alpha=0.7, ax=ax)
            pitch.arrows(shot['location'][0], shot['location'][1], shot['end_location'][0], shot['end_location'][1],
                         width=2, headwidth=10, headlength=10, color='#FF0000',
                         ax=ax)
        for shot in blocked:
            pitch.scatter(shot['location'][0], shot['location'][1], s=(shot['xG'] * 900) + 100, marker='^',
                          edgecolors='black', c='#FF0000', alpha=0.7, ax=ax)
            pitch.arrows(shot['location'][0], shot['location'][1], shot['end_location'][0], shot['end_location'][1],
                         width=2, headwidth=10, headlength=10, color='#FF0000',
                         ax=ax)
        for shot in post:
            pitch.scatter(shot['location'][0], shot['location'][1], s=(shot['xG'] * 900) + 100, marker='s',
                          edgecolors='black', c='#FFFF00', alpha=0.7, ax=ax)
            pitch.arrows(shot['location'][0], shot['location'][1], shot['end_location'][0], shot['end_location'][1],
                         width=2, headwidth=10, headlength=10, color='#FFFF00',
                         ax=ax)
        for shot in onTarget:
            pitch.scatter(shot['location'][0], shot['location'][1], s=(shot['xG'] * 900) + 100, marker='s',
                          edgecolors='black', c='#0000FF', alpha=0.7, ax=ax)
            pitch.arrows(shot['location'][0], shot['location'][1], shot['end_location'][0], shot['end_location'][1],
                         width=2,headwidth=10, headlength=10, color='#0000FF',
                         ax=ax)
        for shot in goals:
            pitch.scatter(shot['location'][0], shot['location'][1], s=(shot['xG'] * 900) + 100, marker='h',
                          edgecolors='black', c='#00FF00', alpha=0.7, ax=ax)
            pitch.arrows(shot['location'][0], shot['location'][1], shot['end_location'][0], shot['end_location'][1],
                         width=2, headwidth=10, headlength=10, color='#00FF00',
                         ax=ax)



        return fig, ax

    def getStatistics(self):
        data = self.shots
        own_goals_for = self.own_goals['for']

        xGs = 0
        goals = own_goals_for.shape[0]

        attempts = {
            # get number of shots by getting number of rows
            'total': data.shape[0],
            'on_target': 0,
            'post': 0,
            'blocked': 0,
            'off_target': 0,
            'xG': []
        }

        for index, shot in data.iterrows():
            shotOutcome = shot['shot']['outcome']['name']
            xGs = xGs + shot['shot']['statsbomb_xg']
            xGtimestamp = shot['minute']
            xG = {
                'rating': round(shot['shot']['statsbomb_xg'], 2),
                'total': round(xGs, 2),
                'outcome': shot['shot']['outcome']['name'],
                'timestamp': xGtimestamp,
            }
            attempts['xG'].append(xG)
            if shotOutcome == 'Goal':
                goals = goals + 1
                attempts['on_target'] = attempts['on_target'] + 1
            elif shotOutcome == 'Saved':
                attempts['on_target'] = attempts['on_target'] + 1
            elif shotOutcome == 'Blocked':
                attempts['blocked'] = attempts['blocked'] + 1
            elif shotOutcome == 'Off T' or shotOutcome == 'Wayward':
                attempts['off_target'] = attempts['off_target'] + 1
            elif shotOutcome == 'Post':
                attempts['post'] = attempts['post'] + 1

        return {
            'xG': round(xGs, 2),
            'goals': goals,
            'attempts': attempts,
            'own_goals': self.own_goals['against'].shape[0],
        }