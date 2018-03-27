from flask import Flask, make_response, json, request
import sqlite3, psutil, os
import sched, time,  threading

s = sched.scheduler(time.time, time.sleep)
db_address = 'C:/Users/baens/PycharmProjects/workshop/test.db'
logfile_location = 'C:/Users/baens/PycharmProjects/workshop/test.log'
default_number_of_lines = 10
interval = 5
connection = sqlite3.connect(db_address, check_same_thread=False)
app = Flask(__name__, static_url_path="")
connection.cursor().execute("CREATE TABLE IF NOT EXISTS stats (id INTEGER PRIMARY KEY AUTOINCREMENT, CPU VARCHAR(255), RAM VARCHAR(255))")


def do_something():
    c = connection.cursor()
    while (True):
        print(time.ctime())
        cpu = str(psutil.cpu_percent(interval=1, percpu=True))
        ram = str(psutil.virtual_memory())
        c.execute("INSERT into stats (cpu, ram) VALUES (?, ?)", (cpu, ram))
        connection.commit()
        time.sleep(interval)


threading.Timer(0,do_something).start()


def tail(f, n, offset=0):
    avg_line_length = 74
    to_read = n + (offset or 0)

    while 1:
        try:
            f.seek(-(avg_line_length * to_read), 2)
        except IOError:
            # woops.  apparently file is smaller than what we want
            # to step back, go to the beginning instead
            f.seek(0)
        pos = f.tell()
        lines = f.read().splitlines()
        if len(lines) >= to_read or pos == 0:
            return lines[-to_read:offset and -offset or None]
        avg_line_length *= 1.3

@app.route('/', methods=["GET"])
def hello_world():
    c = connection.cursor()
    c.execute("Select * from stats")
    print(c.fetchall())
    return 'Hello World!'


@app.route('/healthcheck', methods=["GET"])
def healthcheck():
    resp = make_response('OK', 200)
    return resp


@app.route('/logs', methods=["GET"])
def get_log():
    return json.jsonify(tail(open(logfile_location,'r'),default_number_of_lines))

@app.route('/logs/<n>', methods=["GET"])
def get_nlogs(n):
    return json.jsonify(tail(open(logfile_location,'r'),int(n)))

@app.route('/stats', methods=["GET"])
def get_stats():
    c = connection.cursor()
    c.execute('Select * from stats')
    res = c.fetchall()
    resp = make_response(json.jsonify(res))
    return resp

@app.route('/blacklist/<id>', methods=["GET"])
def get_blacklist_with_id(id):
    c = connection.cursor()
    c.execute('Select * from blacklistip WHERE id = ?', id)
    res = c.fetchone()
    resp = make_response(json.jsonify(res))
    return resp


@app.route('/blacklist', methods=["GET"])
def get_blacklist():
    c = connection.cursor()
    c.execute('Select * from blacklistip')
    res = c.fetchall()
    resp = make_response(json.jsonify(res))
    return resp


@app.route('/whitelist/<id>', methods=["GET"])
def get_whitelist_with_id(id):
    c = connection.cursor()
    c.execute('Select * from whitelistip WHERE id = ?', id)
    res = c.fetchone()
    resp = make_response(json.jsonify(res))
    return resp


@app.route('/whitelist', methods=["GET"])
def get_whitelist():
    c = connection.cursor()
    c.execute("Select * from whitelistip")
    res = c.fetchall()
    resp = make_response(json.jsonify(res))
    return resp


@app.route('/blacklist', methods=["POST"])
def add_blacklist():
    c = connection.cursor()
    ip = request.get_json()["ip"]
    print(ip)
    c.execute("INSERT into blacklistip (ip) VALUES (?)", [ip])
    connection.commit()
    return "OK"


@app.route('/whitelist', methods=["POST"])
def add_whitelist():
    c = connection.cursor()
    ip = request.get_json()["ip"]
    print(ip)
    res = c.execute('INSERT into whitelistip (ip) VALUES (?)', (ip,))
    connection.commit()
    return "OK"


@app.route('/blacklist/ip/<ip>', methods=["DELETE"])
def remove_blacklist_by_ip(ip):
    c = connection.cursor()
    c.execute('DELETE from blacklistip WHERE ip = ?', ip)
    connection.commit()
    return "OK"


@app.route('/whitelist/ip/<ip>', methods=["DELETE"])
def remove_whitelist_by_ip(ip):
    c = connection.cursor()
    c.execute('DELETE from whitelistip WHERE ip = ?', ip)
    connection.commit()
    return "OK"


@app.route('/blacklist/<id>', methods=["DELETE"])
def remove_blacklist_by_id(id):
    c = connection.cursor()
    c.execute('DELETE from blacklistip WHERE id = ?', (id,))
    connection.commit()
    return "OK"


@app.route('/whitelist/<id>', methods=["DELETE"])
def remove_whitelist_by_id(id):
    c = connection.cursor()
    c.execute('DELETE from whitelistip WHERE id = ?', id)
    connection.commit()
    return "OK"


if __name__ == '__main__':
    app.run()


