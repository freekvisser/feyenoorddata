import flask
from flask import Flask, render_template

app = Flask(__name__)

app.secret_key = 'SOME_SECRET_KEY'


@app.route('/')
def index():
    return render_template('index.html')

#background process happening without any refreshing
@app.route('/test')
def background_process_test():
    player = flask.request.args.get('player')
    flask.session['player'] = player
    return flask.jsonify({"response": player})




app.run(host='0.0.0.0', port=8000, debug=True)