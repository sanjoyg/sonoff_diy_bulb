import json
import requests
import socket
from datetime import datetime
import logging

logger = logging.getLogger("sonoff-diy-bulb")

class sonoff_bulb:
    
    mock_count : int = 0
    
    def __init__(self, name, device_id, mock=False):
        logger.debug("Initializing device name: {}, device_id: {}, mock: {}".format(name, device_id, mock))
        self._name = name
        self._device_id = device_id
        self._url = "http://eWeLink_{}.local:8081".format(device_id)
        self._resolved_url=self._url
        self._last_ip_resolution_time = None

        self._is_available = True
        self._is_on = False
        self._ltype="white"
        self._brightness = 100
        self._ct = 0
        self._rgb = (0,0,0)
        self._mock = mock
        
        if self._mock:
            sonoff_bulb.mock_count = sonoff_bulb.mock_count + 1
            self._my_mock_count = sonoff_bulb.mock_count
            logger.debug("My Mock count : {}".format(self._my_mock_count))
        
        if self._mock:
            logger.info("We are mocked to starting twin...")
            import subprocess
            listen_port = 8080 + self._my_mock_count
            subprocess.Popen(["python3", "custom_components/sonoff_diy_bulb/twin/sonoff_bulb_twin.py",str(listen_port)])
            self._url="http://0.0.0.0:808" + str(self._my_mock_count)
            logger.debug("Set url to : {}".format(self._url))
        logger.debug("Initializing complete...")

    def __str__(self):
        to_return = "device_id      : {}".format(self._device_id) + "\n" 
        to_return = to_return + "name           : {}".format(self._name) + "\n"
        to_return = to_return + "available      : {}".format(self._is_available) + "\n"
        to_return = to_return + "is_on          : {}".format(self._is_on) + "\n"
        to_return = to_return + "ltype          : {}".format(self._ltype) + "\n"
        to_return = to_return + "brightness     : {}".format(self._brightness) + "\n"
        to_return = to_return + "ct             : {}".format(self._ct) + "\n"
        to_return = to_return + "rgb            : {}".format(self._rgb) + "\n"
        to_return = to_return + "mock           : {}".format(self._mock) 

        return to_return

    @property
    def name(self):
        return self._name

    @property
    def device_id(self):
        return self._device_id

    @property
    def is_available(self):
        # If resolution time is more than 10 mins, try resolution again. The reason to that
        # is that mDNS has issues at times
        logger.debug("is_available starting... : {}".format(self._device_id))

        try:

            if self._last_ip_resolution_time is None or (datetime.now() - self._last_ip_resolution_time).seconds > 10*60:
                self.resolve_ip()
            self._is_available = self.ping_device()

        except Exception as ex:
            logger.debug(ex)
            logger.debug("failed at is_available...")
            self._is_available = False

        return self._is_available
        
    @property
    def rgb(self):
        return self._rgb

    @property
    def brightness(self):
        return self._brightness

    @property
    def ct(self):
        return self._ct

    @property
    def ltype(self):
        return self._ltype

    @property
    def is_on(self): 
        bulb_on = False
        return self._is_on

    def ping_device(self):
        logger.debug("Pinging Device... : {}".format(self._device_id))

        if self._mock:
            logger.debug("We are mocked so returning local host...")
            self._resolved_url="http://0.0.0.0:808" + str(self._my_mock_count)
            logger.debug("Set resolved url to : {}".format(self._url))
            return True

        try:

            # expected url format is http://a.b.c.d:port
            device=self._resolved_url.split("//")[1].split(":")[0]
            logger.debug("Will ping : {}".format(device))
            socket.setdefaulttimeout(1)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((device, 8081))
            s.close()
            logger.debug("Ping successful...")

        except Exception as error:
            logger.debug(error)
            logger.debug("Failed to ping...")
            return False

        return True

    def resolve_ip(self):
        logger.debug("Resolving...ip... : {}".format(self._device_id))

        if self._mock:
            logger.debug("We are mocked so resolving to local host...")
            self._resolved_url="http://0.0.0.0:808" + str(self._my_mock_count)
            logger.debug("Set resolved url to : {}".format(self._url))
            return 

        try:

            socket.setdefaulttimeout(1)
            host_to_resolve="eWeLink_{}.local".format(self._device_id)
            address=socket.gethostbyname(host_to_resolve)

            self._last_ip_resolution_time = datetime.now()
            self._resolved_url="http://{}:8081".format(address)
            self._last_ip_resolution_time = datetime.now()

            logger.debug("Resolved to: {}".format(self._resolved_url))

        except Exception as ex:
            logger.debug(ex)
            logger.debug("failed to resolve ip...")
            self._resolved_url=self._url

    def send_request(self, url, req_body):
        logger.debug("Starting send_request for : {} with : {}".format(url, req_body))

        try:
            if self._last_ip_resolution_time is None or (datetime.now() - self._last_ip_resolution_time).seconds > 10*60:
                self.resolve_ip()

            headers =  {"Content-Type":"application/json"}
            req_url = "{}{}".format(self._resolved_url,url)

            logger.debug("Sending to URL: {}".format(req_url))
            logger.debug("Sending request: {}".format(req_body))
            
            response = requests.post(req_url, json=req_body, headers=headers)
            logger.debug("Response Code : {}".format(response.status_code))
            logger.debug("Response JSON : {}".format(response.json()))

            if response.status_code != 200:
                logger.debug("Will return as status code is not 200: {}".format(response.status_code))
                self._is_available = self.ping_device()
                return response.status_code, "{}"

            self._is_available = True

            response_json = response.json()
            if response_json is None or "error" not in response_json:
                logger.error("Invalid return JSON : {}".format(response_json))
                return -1, "{}"
            if response_json["error"] != 0:
                logger.debug("Service called return error : {}".format(response["error"]))
                return -1, "{}"

            logger.debug("Send Request complete.. code: {}, response : {}".format(response.status_code, response_json))

            return response.status_code, response_json

        except Exception as ex:
            logger.debug(ex)
            logger.debug("Failed to send request....")
            return 404, "{}"


    def refresh(self):
        return self.set_state()

    def set_state(self):
        logger.debug("Getting State... : {}".format(self._device_id))
        req_body = {"deviceid":self._device_id, "data":{}}
        code, json_ret = self.send_request("/zeroconf/info",req_body)

        if code != 200:
            self._is_available = self.ping_device()
            logger.debug("Return Code is not 200 : {}, returning...".format(code))
            return False

        if json_ret is None:
            return

        if "data" in json_ret:
            data = json_ret["data"]

            if "switch" in data:
                self._is_on = data["switch"] == "on"

            self._ltype = data["ltype"] if "ltype" in data else self._ltype
            
            if "white" in data:
                ltype_data = data["white"]
                # Set Brightness only if ltype matches
                if "white" == self._ltype:
                    self._brightness = ltype_data["br"] if "br" in ltype_data else self._brightness
                    self._ct = ltype_data["ct"] if "ct" in ltype_data else self._ct

            if "color" in data:
                ltype_data = data["color"]
                # Set Brightness only if ltype matches
                if "color" == self._ltype:
                    self._brightness = ltype_data["br"] if "br" in ltype_data else self._brightness
                r = ltype_data["r"] if "r" in ltype_data else self._rgb[0]
                g = ltype_data["g"] if "g" in ltype_data else self._rgb[1]
                b = ltype_data["b"] if "b" in ltype_data else self._rgb[2]
                self._rgb=(r,g,b)
        
        logger.debug(str(self))
        return True

    def switch_on(self):
        logger.debug("Switching On Device...: {}".format(self._device_id))

        json_cmd = { "deviceid" : self._device_id, "data" : { "switch" : "on" } }

        code, data= self.send_request("/zeroconf/switch",json_cmd)
        if code != 200:
            logger.debug("Return Code is not 200 : {}, returning...".format(code))
            return False

        self._is_on = True

    def switch_off(self):
        logger.debug("Switching Off Device...: {}".format(self._device_id))

        json_cmd = { "deviceid" : self._device_id, "data" : { "switch" : "off" } }

        code, data= self.send_request("/zeroconf/switch",json_cmd)
        if code != 200:
            logger.debug("Return Code is not 200 : {}, returning...".format(code))
            return False

        self._is_on = False

    def set_white(self, brightness):
        logger.debug("Setting White Device...: {}".format(self._device_id))

        br = sonoff_bulb.normalize_value(brightness, 0, 100)
        
        # First send turn_on only if brightness is not zero
        if br != 0:
            self.switch_on()
            
        json_cmd = { "deviceid" : self._device_id, "data" : { "ltype" : "white", "white" : {"br" : br, "ct" : self._ct }}}

        code, data= self.send_request("/zeroconf/dimmable", json_cmd)
        if code != 200:
            logger.debug("Return Code is not 200 : {}, returning...".format(code))
            return False

        self._ltype = "white"
        self._brightness = br

        return True

    def set_rgb(self, r, g, b):
        logger.debug("Setting RGB Device...: {}, RGB : {}".format(self._device_id,(r,g,b)))

        r_n = sonoff_bulb.normalize_value(r, 0, 255)
        g_n = sonoff_bulb.normalize_value(g, 0, 255)
        b_n = sonoff_bulb.normalize_value(b, 0, 255)

        # First send turn_on 
        self.switch_on()
            
        json_cmd = { "deviceid" : self._device_id, "data" : { "switch": "on", "ltype" : "color", "color": {"br" : self.brightness, "r" : r_n, "g" : g_n, "b" : b_n }}}

        code, data= self.send_request("/zeroconf/dimmable", json_cmd)
        if code != 200:
            logger.debug("Return Code is not 200 : {}, returning...".format(code))
            return

        self._rgb=(r_n, g_n, b_n)
        self._ltype="color"
        self._is_on = True 

    def set_brightness(self, brightness):
        logger.debug("Setting Brightness for Device...: {} with {}".format(self._device_id, brightness))

        br = sonoff_bulb.normalize_value(brightness, 0, 100)
        
        # First send turn_on only if brightness is not zero
        if br != 0:
            self.switch_on()
            
        json_cmd = { "deviceid" : self._device_id, "data" : { } }

        if self.ltype == "white":
            json_cmd["data"] =  { "switch": "on", "ltype" : "white", "white" : {"br" : br, "ct" : self.ct }}
        else:
            json_cmd["data"] =  { "switch": "on", "ltype" : "color", "color" : {"br" : br, "r" : self._rgb[0], "g" : self._rgb[1], "b" : self._rgb[2] }}

        code, data= self.send_request("/zeroconf/dimmable", json_cmd)
        if code != 200:
            logger.debug("Return Code is not 200 : {}, returning...".format(code))
            return

        self._brightness = br
        self._is_on = True 

    def set_ct(self,ct):
        # Color Temp in sonoff only works in white mode so we would force the
        # ltype to be white

        logger.debug("Setting CT Device... : {} with {}".format(self._device_id, ct))

        # First send turn_on only 
        self.switch_on()
            
        ct_to_set = sonoff_bulb.normalize_value(ct, 0, 100)
        json_cmd = { "deviceid" : self._device_id, "data" : { "switch": "on", "ltype" : "white", "white" : { "br" : self.brightness, "ct" : ct_to_set }}}

        code, data= self.send_request("/zeroconf/dimmable", json_cmd)
        if code != 200:
            logger.debug("Return Code is not 200 : {}, returning...".format(code))
            return

        self._ct = ct_to_set
        self._ltype = "white"
        self._is_on = "on"
        
    @staticmethod
    def normalize_value(value, min, max):
        if value >=min and value <= max:
            return value

        if value < min:
            return min

        if value > max:
            return max

if __name__ == "__main__":
    bulb = sonoff_bulb("bulb_name","bulb_test")

