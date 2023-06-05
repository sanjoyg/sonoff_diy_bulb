import unittest
import sonoff_bulb
from unittest.mock import MagicMock
from unittest.mock import patch
from sonoff_bulb import sonoff_bulb
from datetime import datetime

class sonoff_bulb_test_suite(unittest.TestCase):
    
    @patch('socket.gethostbyname')
    @patch('socket.socket.connect')
    @patch('requests.post')
    def test_set_brightness(self, mock_requests_post, mock_sock_connect, mock_gethostbyname):
        mock_gethostbyname.return_value = "0.0.0.0"

        bulb = sonoff_bulb("bulb_name","bulb_test")

        bulb.send_request = MagicMock(return_value=[200,{}])

        bulb.set_brightness(50)
        url_expected="/zeroconf/dimmable"
        req_expected={"deviceid" : "bulb_test", "data": { "ltype": "white", "white": {"br": 50, "ct": 0 }}}

        bulb.send_request.assert_called_with(url_expected, req_expected)
        self.assertEqual(bulb.brightness,50)
        self.assertEqual(bulb.ct,0)
        self.assertEqual(bulb.ltype,"white")

        bulb.set_brightness(-1)
        url_expected="/zeroconf/dimmable"
        req_expected={"deviceid" : "bulb_test", "data": { "ltype": "white", "white": {"br": 0, "ct": 0 }}}

        bulb.send_request.assert_called_with(url_expected, req_expected)
        self.assertEqual(bulb.brightness,0)
        self.assertEqual(bulb.ct,0)
        self.assertEqual(bulb.ltype,"white")

        bulb.set_brightness(101)
        url_expected="/zeroconf/dimmable"
        req_expected={"deviceid" : "bulb_test", "data": { "ltype": "white", "white": {"br": 100, "ct": 0 }}}

        bulb.send_request.assert_called_with(url_expected, req_expected)
        self.assertEqual(bulb.brightness,100)
        self.assertEqual(bulb.ct,0)
        self.assertEqual(bulb.ltype,"white")

        bulb.set_rgb(10,20,30)
        bulb.set_brightness(70)
        url_expected="/zeroconf/dimmable"
        req_expected={"deviceid" : "bulb_test", "data": { "ltype": "color", "color": {"br": 70, "r": 10, "g" : 20, "b" : 30 }}}

        bulb.send_request.assert_called_with(url_expected, req_expected)
        self.assertEqual(bulb.brightness,70)
        self.assertEqual(bulb.ct,0)
        self.assertEqual(bulb.ltype,"color")

        # On failure retain old value
        bulb.set_white(100)
        bulb.send_request = MagicMock(return_value=[300,{}])
        bulb.set_brightness(60)
        url_expected="/zeroconf/dimmable"
        req_expected={"deviceid" : "bulb_test", "data": { "ltype": "white", "white": {"br": 60, "ct": 0 }}}

        bulb.send_request.assert_called_with(url_expected, req_expected)
        self.assertEqual(bulb.brightness,100)
        self.assertEqual(bulb.ct,0)
        self.assertEqual(bulb.ltype,"white")

if __name__ == '__main__':
    unittest.main()
