# todo make migrations migrate

from datetime import date
from flask import Flask, redirect, url_for, request, render_template
from flask_sqlalchemy import SQLAlchemy
from forms import MamosNetworkForm
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import asc

import json
import requests
import os
import time
import atexit

SECRET_KEY = os.urandom(32)

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///monitor.sqlite3'

sql_db = SQLAlchemy(app)


class MamosNetwork(sql_db.Model):
    ip = sql_db.Column(sql_db.String(120), unique=True, nullable=True, primary_key=True)
    name = sql_db.Column(sql_db.String(120), unique=True, nullable=True)

    def __repr__(self):
        return '<MamosNetwork %r>' % self.ip


headings_main = ("IP", "名前", "消す")
headings = ("名前", "品目１", "品目２", "品目３", "品目４", "品目５", "品目６", "品目７", "異常１", "異常２", "異常３")


def check_online_ip(ip):
    try:
        r = requests.get("http://%s/image_monitor1" % ip, timeout=3)
    except:
        return False
    if 200 == r.status_code:
        return True
    else:
        return False


def take_second(elem):
    return elem[1]


def db_load():
    try:
        sql_ips = MamosNetwork.query.with_entities(MamosNetwork.ip).order_by(asc(MamosNetwork.name))
        sql_name = MamosNetwork.query.with_entities(MamosNetwork.name).order_by(asc(MamosNetwork.name))
    except:
        sql_ips = []
        sql_name = []

    output = []
    for ip, name in zip(sql_ips, sql_name):
        if check_online_ip(ip[0]):
            output.append([ip[0], name[0]])
    return output


def download_api_date(ip, date):
    try:
        r = requests.get("http://%s/download_api?date=%s" % (ip, date), timeout=3).json()
    except:
        print("download_api request error", ip)
        return {}
    return r


def json2data(db, ips, edit=False):
    data = []
    for ip in ips:
        if edit:
            cur = [ip, db[ip]["name"]]
        else:
            cur = [db[ip]["name"]] + db[ip]["product"] + db[ip]["alarm"]
        data.append(tuple(cur))
    return data


@app.route('/', methods=['POST', 'GET'])
def main():
    form = MamosNetworkForm()
    print(">>", request)
    db_data = db_load()

    if request.method == 'POST':
        if form.validate_on_submit():
            if request.form['submit_button'] == '追加':
                try:
                    today = date.today()
                    api_result = download_api_date(form.ip.data, today.strftime("%Y-%m-%d"))
                    if api_result:
                        name = api_result["name"]
                        add_data = MamosNetwork(ip=form.ip.data, name=name)
                        sql_db.session.add(add_data)
                        sql_db.session.commit()
                        db_data.append([form.ip.data, name])
                        db_data.sort(key=take_second)
                except:
                    return "", 504
                return render_template("main.html", headings=headings_main, data=db_data, form=form)
        else:
            result = request.json
            if result:
                if "remove_name" in result:
                    remove_name = result["remove_name"]
                    if remove_name:
                        MamosNetwork.query.filter(MamosNetwork.name == remove_name).delete()
                        sql_db.session.commit()
                    return '', 200
            return '', 502
    else:
        return render_template("main.html", headings=headings_main, data=db_data, form=form)


def query_realtime_today():
    ips = [col[0] for col in db_load()]
    db = {}

    today = date.today()

    for ip in ips:
        api_result = download_api_date(ip, today.strftime("%Y-%m-%d"))
        if api_result:
            db[ip] = api_result
    today.strftime("%Y-%m-%d")
    with open('static/data.json', 'w') as outfile:
        json.dump(db, outfile)
    return '', 200


@app.route('/date', methods=['GET'])
def monitor():
    form = MamosNetworkForm()
    ips = [col[0] for col in db_load()]
    db = {}

    date = "%s-%s-%s" % (
        request.values["check_date"].split("/")[2],
        request.values["check_date"].split("/")[0],
        request.values["check_date"].split("/")[1])

    for ip in ips:
        api_result = download_api_date(ip, date)
        if api_result:
            db[ip] = api_result

    data = {"date": date, "log": json2data(db, ips)}

    return render_template("table.html", headings=headings, data=data, form=form)


if __name__ == '__main__':
    if True:
        scheduler = BackgroundScheduler()
        # calling data delay 30 sec
        scheduler.add_job(func=query_realtime_today, trigger="interval", seconds=30)
        scheduler.start()

        # Shut down the scheduler when exiting the app
        atexit.register(lambda: scheduler.shutdown())

    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
    # app.run(host='192.168.8.100', port=5000, debug=True)
    # app.run(host='172.18.1.100', port=5000, debug=True)
