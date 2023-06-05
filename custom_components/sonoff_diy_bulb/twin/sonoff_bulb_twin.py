import sys
from flask import Flask
from flask import request
import logging
from flask import send_from_directory

logger = logging.getLogger("sonoff-diy-bulb-twin")

logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s : %(levelname)8s : %(message)s","%m-%d %H:%M:%S")
ch.setFormatter(formatter)
logger.addHandler(ch)

app = Flask(__name__)

class sonoff_bulb_twin:
    def __init__(self, name, device_id):
        self._name = name
        self._device_id = device_id
        self._is_on = False
        self._ltype="white"
        self._brightness = 100
        self._ct = 0
        self._rgb = [0,0,0]
        logger.debug("Initializing complete...")
        
    def __str__(self):
        to_return = "\n"
        to_return = to_return + "device_id      : {}".format(self._device_id) + "\n" 
        to_return = to_return + "name           : {}".format(self._name) + "\n"
        to_return = to_return + "is_on          : {}".format(self._is_on) + "\n"
        to_return = to_return + "ltype          : {}".format(self._ltype) + "\n"
        to_return = to_return + "brightness     : {}".format(self._brightness) + "\n"
        to_return = to_return + "ct             : {}".format(self._ct) + "\n"
        to_return = to_return + "rgb            : {}".format(self._rgb) + "\n"
        return to_return

    @property
    def name(self):
        return self._name

    @property
    def device_id(self):
        return self._device_id

    @property
    def is_on(self):
        return self._is_on

    @property
    def ltype(self):
        return self._ltype

    @property
    def brightness(self):
        return self._brightness

    @property
    def rgb(self):
        return self._rgb

    @property
    def ct(self):
        return self._ct

    def make_response_body(self):
        req_body = {}
        req_body["error"] = 0
        req_body["data"] = {}
        req_body["data"]["switch"] = "on" if self._is_on else "off"
        req_body["data"]["ltype"] = self._ltype
        req_body["data"][self._ltype] = {}
        if self._ltype == "white":
            req_body["data"][self._ltype]["br"] = self._brightness
            req_body["data"][self._ltype]["ct"] = self._ct
        elif self._ltype == "color":
            req_body["data"][self._ltype]["br"] = self._brightness
            req_body["data"][self._ltype]["r"] = self._rgb[0]
            req_body["data"][self._ltype]["g"] = self._rgb[1]
            req_body["data"][self._ltype]["b"] = self._rgb[2]

        return req_body

twin_bulb = sonoff_bulb_twin("bulb_name","bulb_device_id")

@app.route("/zeroconf/info", methods=['POST'])
def info():
    try:
        logger.info("/zerconf/info request...")
        data = request.json
        logger.info(data)
        return twin_bulb.make_response_body(), 200
    except Exception as ex:
        logger.error(ex)
        logger.error("Failed to fulfill request...")
        return { "error" : 1, "ex": str(ex) }, 401
    
@app.route("/zeroconf/switch", methods=['POST'])
def switch():
    try:
        logger.info("/zerconf/switch request...")
        logger.info(request.json)

        data = request.json 
        twin_bulb._is_on = True if data["data"]["switch"] == "on" else False
    except Exception as ex:
        logger.error(ex)
        logger.error("Failed to fulfill request...")
        return { "error" : 1, "ex": str(ex) }, 401

    return { "error" : 0 }, 200

@app.route("/zeroconf/dimmable", methods=['POST'])
def dimmable():
    
    try:
        data = request.json

        data_dict = data["data"]
        twin_bulb._ltype = data_dict["ltype"]

        if "white" in data_dict:
            twin_bulb._brightness = data_dict["white"]["br"]
            twin_bulb._ct = data_dict["white"]["ct"]
        elif "color" in data_dict:
            twin_bulb._brightness = data_dict["color"]["br"]
            r=g=b=0
            r = data_dict["color"]["r"]
            g = data_dict["color"]["g"]
            b = data_dict["color"]["b"]
            twin_bulb._rgb=(r,g,b)

        logger.info(twin_bulb)

    except Exception as ex:
        logger.error(ex)
        logger.error("Failed to fulfill request...")
        return { "error" : 1, "ex": str(ex) }, 401

    return { "error" : 0 }, 200

@app.route('/visualize/<path:path>')
def send_report(path):
    return send_from_directory('html', path)

if __name__ == '__main__':
    
    listen_port = 8081

    if len(sys.argv) > 1:
        try:
            listen_port = int(sys.argv[1])
        except:
            pass
    app.run(host="0.0.0.0", port=listen_port)
