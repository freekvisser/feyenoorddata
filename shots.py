from mplsoccer.pitch import VerticalPitch, Pitch

class Shots:
    def __init__(self, data):
        self.d = data

    def drawPitch(self):
        data = self.d
        pitch = VerticalPitch(half=True)
        fig, ax = pitch.draw()

        shots = []
        goals = []

        for index, row in data.iterrows():
            shot = row['shot']
            xG = shot['statsbomb_xg']
            location = row['location']
            data = {
                'xG': xG,
                'location': location
            }

            goals.append(data) if shot['outcome']['name'] == 'Goal' else shots.append(data)

        for shot in shots:
            pitch.scatter(shot['location'][0], shot['location'][1], s=(shot['xG'] * 900) + 100, marker='^',
                          edgecolors='black', c='#ff0000', alpha=0.7, ax=ax)

        for goal in goals:
            pitch.scatter(goal['location'][0], goal['location'][1], s=(goal['xG'] * 900) + 100, marker='h',
                          edgecolors='black', c='#00FF00', alpha=0.7, ax=ax)

        return fig, ax

    def getStatistics(self):
        data = self.d

        xGs = 0
        goals = 0

        attempts = {
            # get number of shots by getting number of rows
            'total': data.shape[0],
            'on_target': 0,
            'blocked': 0
        }

        for index, shot in data.iterrows():
            shotOutcome = shot['shot']['outcome']['name']
            xGs = xGs + shot['shot']['statsbomb_xg']
            if shotOutcome == 'Goal':
                goals = goals + 1
                attempts['on_target'] = attempts['on_target'] + 1
            elif shotOutcome == 'Saved':
                attempts['on_target'] = attempts['on_target'] + 1
            elif shotOutcome == 'Blocked':
                attempts['blocked'] = attempts['blocked'] + 1

        return {
            'xG': round(xGs, 2),
            'goals': goals,
            'attempts': attempts,
        }