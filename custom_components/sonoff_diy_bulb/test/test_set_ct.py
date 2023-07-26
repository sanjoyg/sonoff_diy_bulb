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
    def test_set_ct(self, mock_requests_post, mock_sock_connect, mock_gethostbyname):
        mock_gethostbyname.return_value = "0.0.0.0"

        bulb = sonoff_bulb("bulb_name","bulb_test")

        bulb.send_request = MagicMock(return_value=[200,{}])

        bulb.set_ct(100)
        url_expected="/zeroconf/dimmable"
        req_expected={"deviceid" : "bulb_test", "data": { "switch": "on", "ltype": "white", "white": {"br": 100, "ct": 100 }}}

        bulb.send_request.assert_called_with(url_expected, req_expected)
        self.assertEqual(bulb.brightness,100)
        self.assertEqual(bulb.ct,100)
        self.assertEqual(bulb.ltype,"white")

        # force change of ltype and then test set_ct
        bulb.set_rgb(10,20,30)
        self.assertEqual(bulb.ltype,"color")

        bulb.set_ct(10)
        url_expected="/zeroconf/dimmable"
        req_expected={"deviceid" : "bulb_test", "data": { "switch": "on", "ltype": "white", "white": {"br": 100, "ct": 10 }}}

        bulb.send_request.assert_called_with(url_expected, req_expected)
        self.assertEqual(bulb.brightness,100)
        self.assertEqual(bulb.ct,10)
        self.assertEqual(bulb.ltype,"white")

        bulb.set_ct(-1)
        url_expected="/zeroconf/dimmable"
        req_expected={"deviceid" : "bulb_test", "data": { "switch": "on", "ltype": "white", "white": {"br": 100, "ct": 0 }}}

        bulb.send_request.assert_called_with(url_expected, req_expected)
        self.assertEqual(bulb.brightness,100)
        self.assertEqual(bulb.ct,0)
        self.assertEqual(bulb.ltype,"white")

        bulb.set_ct(101)
        url_expected="/zeroconf/dimmable"
        req_expected={"deviceid" : "bulb_test", "data": { "switch": "on", "ltype": "white", "white": {"br": 100, "ct": 100 }}}

        bulb.send_request.assert_called_with(url_expected, req_expected)
        self.assertEqual(bulb.brightness,100)
        self.assertEqual(bulb.ct,100)
        self.assertEqual(bulb.ltype,"white")

        # Fail resolution, last values should be retained
        bulb.send_request = MagicMock(return_value=[400,{}])

        bulb.set_ct(20)
        url_expected="/zeroconf/dimmable"
        req_expected={"deviceid" : "bulb_test", "data": { "switch": "on", "ltype": "white", "white": {"br": 100, "ct": 20 }}}

        bulb.send_request.assert_called_with(url_expected, req_expected)
        self.assertEqual(bulb.brightness,100)
        self.assertEqual(bulb.ct,100)
        self.assertEqual(bulb.ltype,"white")

        # Pass resolution to set rgb
        bulb.send_request = MagicMock(return_value=[200,{}])
        bulb.set_ct(50)
        bulb.set_rgb(10,20,30)
        self.assertEqual(bulb.ltype,"color")

        # now fail it
        bulb.send_request = MagicMock(return_value=[400,{}])
        bulb.set_ct(75)
        self.assertEqual(bulb.ct,50)
        self.assertEqual(bulb.ltype,"color")

if __name__ == '__main__':
    unittest.main()
