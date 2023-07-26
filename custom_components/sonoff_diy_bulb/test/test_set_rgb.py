import unittest
import sonoff_bulb
from unittest.mock import MagicMock
from unittest.mock import patch
from sonoff_bulb import sonoff_bulb
from datetime import datetime
import json

class sonoff_bulb_test_suite(unittest.TestCase):
    
    @patch('socket.gethostbyname')
    @patch('socket.socket.connect')
    @patch('requests.post')
    def test_set_rgb(self, mock_requests_post, mock_sock_connect, mock_gethostbyname):

        mock_gethostbyname.return_value = "0.0.0.0"
        bulb = sonoff_bulb("bulb_name","bulb_test")

        bulb.send_request = MagicMock(return_value=[200,{}])

        bulb.set_rgb(11,22,33)
        url_expected="/zeroconf/dimmable"
        req_expected={"deviceid" : "bulb_test", "data": { "switch": "on", "ltype": "color", "color": {"br": 100, "r": 11, "g": 22,  "b": 33}}}
        headers={"Content-Type": "application/json"}

        bulb.send_request.assert_called_with(url_expected, req_expected)
        self.assertEqual(bulb.rgb,(11,22,33))
        self.assertEqual(bulb.brightness,100)
        self.assertEqual(bulb.ltype,"color")
        self.assertEqual(bulb.ct,0)

        bulb.set_rgb(-1,22,33)
        url_expected="/zeroconf/dimmable"
        req_expected={"deviceid" : "bulb_test", "data": { "switch": "on", "ltype": "color", "color": {"br": 100, "r": 0, "g": 22,  "b": 33}}}
        headers={"Content-Type": "application/json"}

        bulb.send_request.assert_called_with(url_expected, req_expected)
        self.assertEqual(bulb.rgb,(0,22,33))
        self.assertEqual(bulb.brightness,100)
        self.assertEqual(bulb.ltype,"color")
        self.assertEqual(bulb.ct,0)

        bulb.set_rgb(11,-1,33)
        url_expected="/zeroconf/dimmable"
        req_expected={"deviceid" : "bulb_test", "data": { "switch": "on", "ltype": "color", "color": {"br": 100, "r": 11, "g": 0,  "b": 33}}}
        headers={"Content-Type": "application/json"}

        bulb.send_request.assert_called_with(url_expected, req_expected)
        self.assertEqual(bulb.rgb,(11,0,33))
        self.assertEqual(bulb.brightness,100)
        self.assertEqual(bulb.ltype,"color")
        self.assertEqual(bulb.ct,0)

        bulb.set_rgb(11,22,-1)
        url_expected="/zeroconf/dimmable"
        req_expected={"deviceid" : "bulb_test", "data": { "switch": "on", "ltype": "color", "color": {"br": 100, "r": 11, "g": 22,  "b": 0}}}
        headers={"Content-Type": "application/json"}

        bulb.send_request.assert_called_with(url_expected, req_expected)
        self.assertEqual(bulb.rgb,(11,22,0))
        self.assertEqual(bulb.brightness,100)
        self.assertEqual(bulb.ltype,"color")
        self.assertEqual(bulb.ct,0)

        bulb.set_rgb(256,22,33)
        url_expected="/zeroconf/dimmable"
        req_expected={"deviceid" : "bulb_test", "data": { "switch": "on", "ltype": "color", "color": {"br": 100, "r": 255, "g": 22,  "b": 33}}}
        headers={"Content-Type": "application/json"}

        bulb.send_request.assert_called_with(url_expected, req_expected)
        self.assertEqual(bulb.rgb,(255,22,33))
        self.assertEqual(bulb.brightness,100)
        self.assertEqual(bulb.ltype,"color")
        self.assertEqual(bulb.ct,0)

        bulb.set_rgb(11,256,33)
        url_expected="/zeroconf/dimmable"
        req_expected={"deviceid" : "bulb_test", "data": { "switch": "on", "ltype": "color", "color": {"br": 100, "r": 11, "g": 255,  "b": 33}}}
        headers={"Content-Type": "application/json"}

        bulb.send_request.assert_called_with(url_expected, req_expected)
        self.assertEqual(bulb.rgb,(11,255,33))
        self.assertEqual(bulb.brightness,100)
        self.assertEqual(bulb.ltype,"color")
        self.assertEqual(bulb.ct,0)

        bulb.set_rgb(11,22,256)
        url_expected="/zeroconf/dimmable"
        req_expected={"deviceid" : "bulb_test", "data": { "switch": "on", "ltype": "color", "color": {"br": 100, "r": 11, "g": 22,  "b": 255}}}
        headers={"Content-Type": "application/json"}

        bulb.send_request.assert_called_with(url_expected, req_expected)
        self.assertEqual(bulb.rgb,(11,22,255))
        self.assertEqual(bulb.brightness,100)
        self.assertEqual(bulb.ltype,"color")
        self.assertEqual(bulb.ct,0)

        #Now fail the send_request to ensure that previous values are retained
        bulb.send_request = MagicMock(return_value=[400,{}])
        bulb.set_rgb(10,20,30)
        self.assertEqual(bulb.rgb,(11,22,255))
        self.assertEqual(bulb.ltype,"color")

        # Set white, then set fail then set rgb to check retained old value
        bulb.send_request = MagicMock(return_value=[200,{}])
        bulb.set_white(90)
        self.assertEqual(bulb.ltype,"white")
        bulb.send_request = MagicMock(return_value=[400,{}])
        bulb.set_rgb(11,22,33)
        self.assertEqual(bulb.brightness,90)
        self.assertEqual(bulb.ltype,"white")


if __name__ == '__main__':
    unittest.main()
