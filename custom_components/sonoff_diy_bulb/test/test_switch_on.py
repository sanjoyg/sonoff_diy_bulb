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
    def test_switch_on(self,mock_requests_post, mock_sock_connect, mock_gethostbyname):
        mock_gethostbyname.return_value = "0.0.0.0"

        bulb = sonoff_bulb("bulb_name","bulb_test")

        bulb.send_request = MagicMock(return_value=[200,{}])

        bulb.switch_on()
        url_expected="/zeroconf/switch"
        req_expected={"deviceid" : "bulb_test", "data": { "switch": "on" }}

        bulb.send_request.assert_called_with(url_expected, req_expected)
        self.assertEqual(bulb.is_on,True)

        # Now fail, and old should retain after ON
        bulb.switch_off()
        self.assertEqual(bulb.is_on,False)
        bulb.send_request = MagicMock(return_value=[300,{}])
        bulb.switch_on()
        url_expected="/zeroconf/switch"
        req_expected={"deviceid" : "bulb_test", "data": { "switch": "on" }}

        bulb.send_request.assert_called_with(url_expected, req_expected)
        self.assertEqual(bulb.is_on, False)

if __name__ == '__main__':
    unittest.main()
