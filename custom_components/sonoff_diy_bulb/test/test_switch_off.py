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
    def test_switch_off(self,mock_requests_post, mock_sock_connect, mock_gethostbyname):
        mock_gethostbyname.return_value = "0.0.0.0"

        bulb = sonoff_bulb("bulb_name","bulb_test")

        bulb.send_request = MagicMock(return_value=[200,{}])

        bulb.switch_off()
        url_expected="/zeroconf/switch"
        req_expected={"deviceid" : "bulb_test", "data": { "switch": "off" }}

        bulb.send_request.assert_called_with(url_expected, req_expected)
        self.assertEqual(bulb.is_on,False)

        # Now fail, and old should retain after ON
        bulb.switch_on()
        self.assertEqual(bulb.is_on,True)
        bulb.send_request = MagicMock(return_value=[300,{}])
        bulb.switch_off()
        url_expected="/zeroconf/switch"
        req_expected={"deviceid" : "bulb_test", "data": { "switch": "off" }}

        bulb.send_request.assert_called_with(url_expected, req_expected)
        self.assertEqual(bulb.is_on, True)

if __name__ == '__main__':
    unittest.main()
