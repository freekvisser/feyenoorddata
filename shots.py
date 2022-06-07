from mplsoccer.pitch import VerticalPitch, Pitch

class Shots:
    def __init__(self, data):
        self.d = data

    def drawPitch(self):
        data = self.d
        pitch = VerticalPitch(half=True)
        fig, ax = pitch.draw()

        for index, row in data.iterrows():
            team = row['team']
            shot = row['shot']
            location = row['location']
            print(team['name'], shot['statsbomb_xg'], location)
            pitch.scatter(location[0], location[1], s=(shot['statsbomb_xg'] * 900) + 100, edgecolors='black', ax=ax)





        return fig, ax