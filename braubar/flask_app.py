# -*- coding: utf-8 -*-
import os
import datetime

from flask import Flask, jsonify, render_template
from service.chartService import ChartService
import brewconfig

__author__ = 'oli@fesseler.info'
__version__ = ('0', '0', '1')

app = Flask(__name__)


@app.route("/")
def index():
    status = ChartService.last_row(brew_id)
    # 2016-01-08T00:44:47.848484
    brew_time = datetime.datetime.strptime(status["brew_time"], "%Y-%m-%dT%H:%M:%S.%f")
    brew_start = datetime.datetime.fromtimestamp(status["brew_id"]/1000.0)
    duration = (brew_time - brew_start)
    status["duration"] = str(duration).split(".")[0]
    status["temp_increase"] = ChartService.temp_increase(brew_id)

    return render_template('index.html', brew_id=brew_id, brew_state=status)


@app.route('/start')
def brewStart():
    return "Not Implemented"


@app.route('/status/brew')
def brew_state():
    return ChartService.brew_status(brew_id=brew_id)


@app.route('/status/system')
def system_state():
    return ChartService.system_status(brew_id=brew_id)


@app.route('/next')
def next():
    asd = None
    try:
        os.system("echo 'True' > " + brewconfig.NEXT_STATE_FILE)
        asd = {"ok": True, "state": None}
    except:
        print("next failed")
        asd = {"ok": False, "state": None}
    finally:
        return jsonify(asd)


@app.route('/temp')
def temp():
    return "Not Implemented"


@app.route('/chart/data')
def chart_data():
    return ChartService.brew_chart(brew_id=brew_id)


@app.route('/chart/last_row')
def last_row():
    return jsonify(ChartService.last_row(brew_id=brew_id))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="BrauBar webserver at your service.")
    parser.add_argument('--host', help="IP-Address to listen on. Default is 0.0.0.0", default="0.0.0.0")
    parser.add_argument('-i', '--id', help="brew_id to identify the current brew process. "
                                           "if no id is given, it shall return all brews")
    args = parser.parse_args()
    try:
        host = args.host
        brew_id = args.id
        # start app in debugmode
        app.debug = True
        app.run(host=host)
    finally:
        print("good beer, see ya")
