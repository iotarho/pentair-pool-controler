"""
The flask server for the pool_controller
Michael Usner
"""
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify, request
from pool_controller import PentairCom


host_ip = "0.0.0.0"
host_port = "8080"
flask_app = Flask(__name__)
pool = PentairCom("/dev/ttyS0", logger=flask_app.logger)
pool.start()


def no_cache(ret):
    """ No Cache function """
    ret.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    ret.headers["Pragma"] = "no-cache"
    ret.headers["Expires"] = 0
    return ret

@flask_app.route("/metrics",methods=["GET"])
def get_monitor():
    """ Build monitoring interface for Promethius """
    flask_app.logger.info("%s: /metrics", request.remote_addr)
    ret = pool.get_status()
    monitor="Pump1_watts {}".format(ret.get("Pump1_watts"))
    monitor+="\nPump1_rpm {}".format(ret.get("Pump1_rpm"))
    monitor+="\nPump2_watts {}".format(ret.get("Pump1_watts"))
    monitor+="\nPump2_rpm {}".format(ret.get("Pump1_rpm"))
    monitor+="\nPump3_watts {}".format(ret.get("Pump3_watts"))
    monitor+="\nPump3_rpm {}".format(ret.get("Pump3_rpm"))
    monitor+="\nPump4_watts {}".format(ret.get("Pump4_watts"))
    monitor+="\nPump4_rpm {}".format(ret.get("Pump4_rpm"))
    monitor+="\nwater_temp {}".format(ret.get("water_temp"))
    monitor+="\nair_temp {}".format(ret.get("air_temp"))

    flask_app.logger.info("%s: Returning: %s", request.remote_addr, monitor)
    return monitor

@flask_app.route("/pool/status", methods=["GET"])
def get_status():
    """ Get the pool controller status """
    flask_app.logger.info("%s: /pool/status", request.remote_addr)
    ret = jsonify(pool.get_status())
    flask_app.logger.info("%s: Returning: %s", request.remote_addr, ret.response)
    return no_cache(ret)


@flask_app.route("/pool/<feature>/<state>", methods=["GET"])
def set_feature(feature, state):
    """ Set a feature state """
    flask_app.logger.info("%s: /pool/%s/%s", request.remote_addr, feature, state)
    res = pool.send_command(pool.FeatureName[feature], state)
    flask_app.logger.info("%s: Returning %s", request.remote_addr, {feature: res[feature]})
    return no_cache(jsonify({feature: res[feature]}))


def all_off():
    """ Turn everything off """
    pool.send_command("pool", "off")
    pool.send_command("spa", "off")
    pool.send_command("pool_light", "off")
    pool.send_command("spa_light", "off")
    pool.send_command("cleaner", "off")


if __name__ == '__main__':
    handler = RotatingFileHandler('/home/pi/pool/server.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.DEBUG)
    flask_app.logger.addHandler(handler)
    flask_app.run(host=host_ip, port=host_port, debug=False)
