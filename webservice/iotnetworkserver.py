from flask import Flask, jsonify
from flask import request
import logging
from datetime import datetime
import csv
import os.path
import json
import requests
import time

application = Flask(__name__)
#auth = HTTPBasicAuth()
logpath = "/Users/Luix/PycharmProjects/iotelasticproject/"


@application.route('/logstashmetricinput', methods=['POST'])
def insert_metric():
    try:

            url = 'http://127.0.0.1:31311/'
            head = {'Content-type': 'application/json'}
            date = time.strftime("%Y-%m-%d")

            filename = logpath+"inputmetric_"+date+".cvs"
            idnode = str(request.json['idnode'])
            sequencenum = str(request.json['sequencenum'])
            snr = str(request.json['snr'])
            rssi = str(request.json['rssi'])
            temperature = str(request.json['temperature'])
            umidity = str(request.json['umidity'])
            latitude = str(request.json['latitude'])
            longitude = str(request.json['longitude'])
            nodelocation = str(latitude)+","+str(longitude)
            delay = str(request.json['delay'])
            lorasetup = str(request.json['lorasetup'])
            packetsize = str(request.json['packetsize'])
            expid = str(request.json['experimentid'])
            gwlocation = str(request.json['gw-location'])
            timestamp = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

            payload = {'sensorId':idnode,'sequenceNumber':sequencenum,'snr':snr,'rssi':rssi, \
                       'temperature':temperature,'umidity':umidity,'node-location':nodelocation,\
                       'time':timestamp,'delay':delay,'lorasetup':lorasetup,'packetsize':packetsize,'experimentid':expid,'gw-location':gwlocation}
            logger.info(payload);
           # res = requests.post(url,data=json.dumps(payload),headers=head)
           # logger.error(res)
            with open(filename, "aw") as fo:
                 fo.write(timestamp+","+idnode+","+sequencenum +","+snr+","+rssi+","+temperature+",\
                        "+umidity+","+nodelocation+","+delay+","+lorasetup+","+packetsize+","+expid+","+gwlocation+"\n")
            return jsonify({'insert': "ok"}), 200
    except Exception, inst:
        logger.error(inst)

def create_logger():
    global logger
    logger = logging.getLogger(logpath+'iotnetserverlogger')
    hdlr = logging.FileHandler('iotnetserver.log')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.INFO)

if __name__ == '__main__':
    create_logger()
    application.run(debug=True,host='127.0.0.1')
        
