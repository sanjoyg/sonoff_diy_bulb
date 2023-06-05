import unittest
import sonoff_bulb
from unittest.mock import MagicMock
from unittest.mock import patch
from sonoff_bulb import sonoff_bulb
from datetime import datetime

class sonoff_bulb_test_suite(unittest.TestCase):
    
    @patch('socket.gethostbyname')
    @patch('socket.socket.connect')
    def test_ctor(self,mock_sock_connect, mock_gethostbyname):
        mock_gethostbyname.return_value = "0.0.0.0"
        mock_sock_connect.return_value = 0

        # Create object to test
        bulb = sonoff_bulb("bulb_name", "bulb_test")

        # Asserts
        self.assertEqual(bulb._name, "bulb_name")
        self.assertEqual(bulb._device_id, "bulb_test")
        self.assertEqual(bulb._url,"http://eWeLink_bulb_test.local:8081")
        self.assertEqual(bulb._resolved_url,"http://eWeLink_bulb_test.local:8081")
        self.assertEqual(bulb._last_ip_resolution_time,None)

        self.assertEqual(bulb._is_available,True)
        self.assertEqual(bulb._is_on, False)
        self.assertEqual(bulb._brightness, 100)
        self.assertEqual(bulb._ct, 0)
        self.assertEqual(bulb._rgb, (0,0,0))
        self.assertEqual(bulb._ltype, "white")

    @patch('socket.gethostbyname')
    @patch('socket.socket.connect')
    def test_is_available(self,mock_sock_connect, mock_gethostbyname):
        mock_gethostbyname.return_value = "0.0.0.0"
        mock_sock_connect.return_value = 0

        # Create object to test
        bulb = sonoff_bulb("bulb_name", "bulb_test")

        self.assertEqual(bulb.is_available, True)
        self.assertEqual(bulb._resolved_url,"http://0.0.0.0:8081")
        self.assertEqual((datetime.now() - bulb._last_ip_resolution_time).seconds < 2 ,True)

    @patch('socket.gethostbyname')
    @patch('socket.socket.connect')
    def test_is_available_no_resolve(self,mock_sock_connect, mock_gethostbyname):
        mock_gethostbyname.side_effect = Exception("Mock didnt resolve!")
        mock_sock_connect.return_value = 0

        # Create object to test
        bulb = sonoff_bulb("bulb_name","bulb_test")

        # Asserts
        self.assertEqual(bulb.is_available, True)
        self.assertEqual(bulb._last_ip_resolution_time,None)
        self.assertEqual(bulb._resolved_url,"http://eWeLink_bulb_test.local:8081")

    @patch('socket.gethostbyname')
    @patch('socket.socket.connect')
    def test_ctor_no_resolve_no_ping(self,mock_sock_connect, mock_gethostbyname):
        mock_gethostbyname.side_effect = Exception("Mock didnt resolve!")
        mock_sock_connect.side_effect = Exception("Mock didnt allow ping!")

        # Create object to test
        bulb = sonoff_bulb("bulb_name","bulb_test")

        # Asserts
        self.assertEqual(bulb.is_available, False)
        self.assertEqual(bulb._last_ip_resolution_time,None)
        self.assertEqual(bulb._resolved_url,"http://eWeLink_bulb_test.local:8081")

if __name__ == '__main__':
    unittest.main()
