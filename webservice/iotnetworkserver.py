from flask import Flask, jsonify
from flask import request
import logging
from datetime import datetime
import csv
import os.path
import json
import requests
import time
import mpu
application = Flask(__name__)

logpath = "/var/log/iotnetworkserver/"
exppath = "/opt/iotnetworkserver/exp_results/"
logger = logging.getLogger('iotnetserverlogger')
hdlr = logging.FileHandler(logpath+'iotnetserver.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)


@application.route('/logstashmetricinput', methods=['POST'])
def insert_metric():
    try:
            url = 'http://127.0.0.1:31311/'
            head = {'Content-type': 'application/json'}
            date = time.strftime("%Y-%m-%d")
            filename = logpath+"inputmetric_"+date+".cvs"
	    geofile = logpath+"geodistance_"+date+".txt"
            idnode = request.json['idnode']
            sequencenum = request.json['sequencenum']
            snr = str(request.json['snr'])
            rssi = str(request.json['rssi'])
            temperature = str(request.json['temperature'])
            umidity = str(request.json['umidity'])
            latitude = str(request.json['latitude'])
            longitude = str(request.json['longitude'])
            nodelocation = latitude+","+longitude
            delay = str(request.json['delay'])
            lorasetup = str(request.json['lorasetup'])
            packetsize = str(request.json['packetsize'])
            expid = str(request.json['experimentid'])
            gwlocation = str(request.json['gw-location'])
            gwlat = str(gwlocation.split(",")[0])
            gwlon = str(gwlocation.split(",")[1])
            txpower = request.json['txpower']
            throughput = ( float(packetsize) * float(delay) ) / 1000
            rssifile = exppath+"rssi_"+expid+"_"+date+".csv"
            snrfile = exppath+"snr_"+expid+"_"+date+".csv"
            delayfile = exppath+"delay_"+expid+"_"+date+".csv"
            thougfile = exppath+"throughput_"+expid+"_"+date+".csv"
            timestamp = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
	    dist = mpu.haversine_distance((float(latitude), float(longitude)), (float(gwlat),float(gwlon))) * 1000
            payload = {'sensorId':idnode,'sequenceNumber':sequencenum,'snr':snr,'rssi':rssi, \
                       'temperature':temperature,'umidity':umidity,'node-location':nodelocation,\
                       'time':timestamp,'delay':delay,'lorasetup':lorasetup,'packetsize':packetsize,'experimentid':expid,'gw-location':gwlocation,'txpower':txpower,'throughput':throughput}
            res = requests.post(url,data=json.dumps(payload),headers=head)
            logger.info("expid: "+expid+" sequencenum: "+sequencenum+" res: " +res)
            with open(filename, "aw") as fo:
                 fo.write(timestamp+","+idnode+","+sequencenum +","+snr+","+rssi+","+temperature+","+umidity+","+nodelocation+","+delay+","+lorasetup+","+packetsize+","+expid+","+gwlocation+","+txpower+","+str(throughput)+"\n")
	    with open(geofile, "aw") as geo:
		 geo.write(timestamp+","+"EXPID: "+expid+","+"DISTANCE: "+str(dist)+"\n")
	    with open(rssifile, "aw") as rssiFile:
		 rssiFile.write(timestamp+","+rssi+","+str(dist)+"\n")
	    with open(snrfile, "aw") as snrFile:
		 snrFile.write(timestamp+","+snr+","+str(dist)+"\n")
	    with open(delayfile, "aw") as delayFile:
		 delayFile.write(timestamp+","+snr+","+str(dist)+"\n")
	    with open(thougfile, "aw") as througFile:
		 througFile.write(timestamp+","+str(throughput)+","+str(dist)+"\n")

    except Exception, inst:
        print(inst)
        logger.error(inst)
    return jsonify({'insert': "ok"}), 200



if __name__ == '__main__':
    application.run(debug=True,host='127.0.0.1')
