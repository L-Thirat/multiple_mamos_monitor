# todo make migrations migrate


from flask import Flask, redirect, url_for, request, render_template
from flask_sqlalchemy import SQLAlchemy
from forms import MamosNetworkForm

import json
import requests
import os

SECRET_KEY = os.urandom(32)

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///monitor.sqlite3'

sql_db = SQLAlchemy(app)


class MamosNetwork(sql_db.Model):
    id = sql_db.Column(sql_db.Integer, primary_key=True)
    ip = sql_db.Column(sql_db.String(120), unique=True, nullable=True)

    def __repr__(self):
        return '<MamosNetwork %r>' % self.ip


headings = ("Name", "1", "2", "3", "4", "5", "6", "7", "ALARM1", "ALARM2", "ALARM3", "Remove")


def db_load_ips():
    try:
        sql_ips = MamosNetwork.query.with_entities(MamosNetwork.ip).all()
    except:
        sql_ips = []

    ips = []
    for ip in sql_ips:
        ips.append(ip[0])
    return ips


def download_api(db, ip):
    try:
        # for ip in ips:
        r = requests.get("http://%s/download_api" % ip, timeout=3).json()

        db[ip] = r
        with open('static/data.json', 'w') as json_file:
            json.dump(db, json_file)
    except:
        print("download_api request error", ip)
        return False
    return db


def json2data(db, ips):
    data = []
    for ip in ips:
        cur = [db[ip]["name"]] + db[ip]["product"] + db[ip]["alarm"]
        data.append(tuple(cur))
    return data


def load_json():
    with open('static/data.json') as json_file:
        db = json.load(json_file)
    return db


# ips = db_load_ips()
"""
Keep ips in db
load last json
#todo check matching ips
download API
"""


@app.route('/update', methods=['GET'])
def update():
    print(">>", request)
    ips = db_load_ips()
    db = load_json()

    for ip in ips:
        dowload_result = download_api(db, ip)
        if type(dowload_result) != bool:
            db = dowload_result

    with open('static/data.json', 'w') as outfile:
        json.dump(db, outfile)
    return '', 200


@app.route('/', methods=['POST', 'GET'])
def monitor():
    form = MamosNetworkForm()
    print(">>", request)
    ips = db_load_ips()
    db = load_json()

    if request.method == 'POST':
        result = request.json
        print("POST>>", result)
        # db
        if form.validate_on_submit():
            if request.form['submit_button'] == 'Add':
                # m = MamosNetwork()
                # db = load_json()

                form_ips = ips.copy()
                form_ips.append(form.ip.data)
                for ip in form_ips:
                    download_result = download_api(db, ip)
                    if type(download_result) != bool:
                        db = download_result
                        if ip == form.ip.data and ip not in ips:
                            # m.ip = form.ip.data
                            add_data = MamosNetwork(ip=form.ip.data)
                            sql_db.session.add(add_data)
                            sql_db.session.commit()
                            ips.append(ip)
                data = json2data(db, ips)
                return render_template("table.html", headings=headings, data=data, form=form)
        else:
            result = request.json
            print(result)
            # db = load_json()

            for ip in ips:
                dowload_result = download_api(db, ip)
                if type(dowload_result) != bool:
                    db = dowload_result

            if "remove_name" in result:
                new_db = {}
                # new_ips = []
                remove_ip = None
                for k, v in db.items():
                    if v["name"] == result["remove_name"]:
                        remove_ip = k
                    else:
                        new_db[k] = v
                        # new_ips.append(v["ip"])
                db = new_db.copy()
                # write new db
                print(db, remove_ip, result["remove_name"])
                with open('static/data.json', 'w') as outfile:
                    json.dump(db, outfile)
                    if remove_ip:
                        # remove_data = MamosNetwork(ip=remove_ip)
                        # sql_db.session.delete(remove_data)
                        MamosNetwork.query.filter(MamosNetwork.ip == remove_ip).delete()
                        sql_db.session.commit()
                # data = json2data(db, new_ips)
                return '', 200

            else:
                # ajax post to write new  json file when remove
                ip = result["ip"]
                # name = result["name"]

                if ip not in db:
                    db[ip] = {}

                # update db
                for key in result:
                    if key != "ip":
                        db[ip][key] = [str(x) for x in result[key]]

                # write new db
                with open('static/data.json', 'w') as outfile:
                    json.dump(db, outfile)

                return '', 200
    else:
        # db = load_json()

        data = json2data(db, ips)
        return render_template("table.html", headings=headings, data=data, form=form)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    # app.run(host='192.168.8.100', port=5000, debug=True)
    # app.run(host='172.18.1.100', port=5000, debug=True)
