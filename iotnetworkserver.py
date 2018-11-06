from flask import Flask, jsonify
from flask import request
import logging
from datetime import datetime
from elasticsearch import Elasticsearch
import json
import requests
import time
import mpu
import os

application = Flask(__name__)

logpath = "/var/log/iotnetworkserver/"
exppath = "/opt/iotnetworkserver/exp_results/"
logger = logging.getLogger('iotnetserverlogger')
hdlr = logging.FileHandler(logpath + 'iotnetserver.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)
es = Elasticsearch("localhost:9200")


@application.route('/logstashmetricinput', methods=['POST'])
def insert_metric():
    try:
        url = 'http://127.0.0.1:31311/'
        head = {'Content-type': 'application/json'}
        date = time.strftime("%Y-%m-%d")
        today = str(datetime.now().strftime('%Y.%m.%d'))
        index_name = "lora_data-{}".format(today)

        idnode = request.json['idnode']
        sequencenum = request.json['sequencenum']
        snr = str(request.json['snr'])
        rssi = str(request.json['rssi'])
        temperature = str(request.json['temperature'])
        umidity = str(request.json['umidity'])
        latitude = str(request.json['latitude'])
        longitude = str(request.json['longitude'])
        nodelocation = latitude + "," + longitude
        delay = str(request.json['delay'])
        lorasetup = str(request.json['lorasetup'])
        packetsize = str(request.json['packetsize'])
        expid = str(request.json['experimentid'])
        gwlocation = str(request.json['gw-location'])
        gwlat = str(gwlocation.split(",")[0])
        gwlon = str(gwlocation.split(",")[1])
        txpower = request.json['txpower']
        throughput = (float(packetsize) * float(delay)) / 1000
        exppathid = exppath + expid
        timestamp = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        dist = mpu.haversine_distance((float(latitude), float(longitude)), (float(gwlat), float(gwlon))) * 1000
        try:
            if not os.path.exists(exppath+expid):
                os.makedirs(exppathid)
                os.makedirs(exppathid+"/rssi")
                os.makedirs(exppathid+"/snr")
                os.makedirs(exppathid+"/throughput")
                os.makedirs(exppathid+"/pdr")
                os.makedirs(exppathid + "/delay")
        except OSError, inst:
            logger.error ('Error: Creating directory. ' + str(inst))

        rssifile = exppathid + "/rssi/rssi_" + expid + "_" + date + ".csv"
        snrfile = exppathid + "/snr/snr_" + expid + "_" + date + ".csv"
        delayfile = exppathid + "/delay/delay_" + expid + "_" + date + ".csv"
        thougfile = exppathid + "/throughput/throughput_" + expid + "_" + date + ".csv"
        pdrfile = exppathid + "/pdr/pdr_" + expid + "_" + date + ".csv"
        resultfile = exppathid + "/inputmetric_" + expid + "_" + date + ".csv"
        geofile = exppathid + "/geodistance_" + expid + "_" + date + ".txt"
        geologfile = logpath + "geolog.log"
    except Exception, inst:
        print(inst)
        logger.error("Request json exception " + str(inst))

    try:
        query = "experimentid=" + expid
        results = es.search(index=index_name, size=1000, q=query)["hits"]["hits"]
        if len(results) > 0:
            count = len(results)
            sequence = [int(r["_source"]["sequenceNumber"]) for r in results]
            max_sequence = max(sequence)
            pdr = float(count) / max_sequence * 100
        else:
            logger.info("Elasticsearch return empty set")
            pdr = '0'

    except Exception, inst:
        logger.error("Elasticsearch query exception " + str(inst))
        pdr = '0'

    try:
        payload = {'sensorId': idnode, 'sequenceNumber': sequencenum, 'snr': snr, 'rssi': rssi, \
                   'temperature': temperature, 'umidity': umidity, 'node-location': nodelocation, \
                   'time': timestamp, 'delay': delay, 'lorasetup': lorasetup, 'packetsize': packetsize,
                   'experimentid': expid, 'gw-location': gwlocation, 'txpower': txpower, 'throughput': throughput,
                   'distance': str(dist), 'pdr': str(pdr)}
        res = requests.post(url, data=json.dumps(payload), headers=head)
        logger.info("Logstash respone: " + str(res))
    except Exception, inst:
        logger.error("Logstash exception: " + str(inst))
    try:
        with open(resultfile, "aw") as fo:
            fo.write(
                timestamp + "," + idnode + "," + sequencenum + "," + snr + "," + rssi + "," + temperature + "," + umidity + "," + nodelocation + "," + delay + "," + lorasetup + "," + packetsize + "," + expid + "," + gwlocation + "," + txpower + "," + str(
                    throughput) + "," + str(dist) + ","+str(pdr)+"\n")
        with open(geofile, "aw") as geo:
            geo.write(timestamp + "," + "EXPID: " + expid + "," + "DISTANCE: " + str(dist) + "\n")
        with open(rssifile, "aw") as rssiFile:
            rssiFile.write(timestamp + "," + rssi + "," + str(dist) + "\n")
        with open(snrfile, "aw") as snrFile:
            snrFile.write(timestamp + "," + snr + "," + str(dist) + "\n")
        with open(delayfile, "aw") as delayFile:
            delayFile.write(timestamp + "," + delay + "," + str(dist) + "\n")
        with open(thougfile, "aw") as througFile:
            througFile.write(timestamp + "," + str(throughput) + "," + str(dist) + "\n")
        with open(pdrfile, "aw") as pdrFile:
            pdrFile.write(timestamp + "," + str(pdr) + "," + str(dist) + "\n")
        with open(geologfile, "aw") as geolog:
            geolog.write(timestamp + "," + "EXPID: " + expid + "," + "DISTANCE: " + str(dist) + "\n")

    except Exception, inst:
        logger.error("Write files exception " + str(inst))

    return jsonify({'insert': "ok"}), 200


if __name__ == '__main__':
    application.run(debug=True, host='127.0.0.1')
