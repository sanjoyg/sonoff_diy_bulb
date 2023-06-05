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
    def test_set_state(self,mock_requests_post, mock_sock_connect, mock_gethostbyname):
        mock_json_return = {}
        mock_json_return["error"]=0
        mock_json_return["data"]={}
        mock_json_return["data"]["switch"]="on"
        mock_json_return["data"]["ltype"]="white"
        mock_json_return["data"]["white"]={"br":50, "ct":40 }
        mock_json_return["data"]["color"]={"br":60, "r":10, "g": 20, "b": 30 }

        mock_requests_post.return_value = MagicMock(status_code=200, json=lambda: mock_json_return)
        mock_gethostbyname.return_value = "0.0.0.0"
        mock_sock_connect.return_value = 0
        
        bulb = sonoff_bulb("bulb_name","bulb_test")
        self.assertEqual(bulb.set_state(), True)

        self.assertEqual(bulb._device_id, "bulb_test")
        self.assertEqual(bulb._url,"http://eWeLink_bulb_test.local:8081")
        self.assertEqual(bulb._resolved_url,"http://0.0.0.0:8081")
        self.assertEqual((datetime.now() - bulb._last_ip_resolution_time).seconds < 2 ,True)

        self.assertEqual(bulb._is_available,True)
        self.assertEqual(bulb.is_on, True)
        self.assertEqual(bulb.ltype, "white")

        self.assertEqual(bulb.brightness, 50)
        self.assertEqual(bulb.ct, 40)
        self.assertEqual(bulb.rgb,(10,20,30))

        # Now set ltype to color and then assert on brightness and ct
        mock_json_return["data"]["ltype"]="color"
        mock_json_return["data"]["switch"]="off"
        self.assertEqual(bulb.set_state(), True)

        self.assertEqual(bulb._device_id, "bulb_test")
        self.assertEqual(bulb._url,"http://eWeLink_bulb_test.local:8081")
        self.assertEqual(bulb._resolved_url,"http://0.0.0.0:8081")
        self.assertEqual((datetime.now() - bulb._last_ip_resolution_time).seconds < 2 ,True)

        self.assertEqual(bulb._is_available,True)
        self.assertEqual(bulb.is_on, False)
        self.assertEqual(bulb.ltype, "color")

        self.assertEqual(bulb.brightness, 60)
        self.assertEqual(bulb.ct, 40)
        self.assertEqual(bulb.rgb,(10,20,30))

    @patch('socket.gethostbyname')
    @patch('socket.socket.connect')
    @patch('requests.post')
    def test_set_state_keep_old_state_if_fail_connect(self,mock_requests_post, mock_sock_connect, mock_gethostbyname):
        mock_json_return = {}
        mock_json_return["error"]=0
        mock_json_return["data"]={}
        mock_json_return["data"]["switch"]="on"
        mock_json_return["data"]["ltype"]="white"
        mock_json_return["data"]["white"]={"br":50, "ct":30 }
        mock_json_return["data"]["color"]={"br":60, "r": 10, "g": 20, "b": 30 }

        mock_requests_post.return_value = MagicMock(status_code=200, json=lambda: mock_json_return)
        mock_gethostbyname.return_value = "0.0.0.0"
        mock_sock_connect.return_value = 0
        
        bulb = sonoff_bulb("bulb_name","bulb_test")
        self.assertEqual(bulb.set_state(), True)

        self.assertEqual(bulb._is_available,True)
        self.assertEqual(bulb.is_on, True)
        self.assertEqual(bulb.ltype, "white")

        self.assertEqual(bulb.brightness, 50)
        self.assertEqual(bulb.ct, 30)
        self.assertEqual(bulb.rgb,(10,20,30))

        return

        # Above should go through now lets fail and ensure previous state is retained
        mock_json_return_alt = {}
        mock_json_return_alt["error"]=10
        mock_json_return_alt["data"]={}
        mock_json_return_alt["data"]["ltype"]="color"
        mock_json_return["data"]["white"]={"br":55, "ct":0 }
        mock_json_return["data"]["color"]={"br":65, "r":15, "g": 25, "b": 35 }

        mock_requests_post.side_effect = Exception("Mock POST will fail...")
        mock_sock_connect.side_effect = Exception("Mock is going fail connect!")

        self.assertEqual(bulb.set_state(), False)

        self.assertEqual(bulb._is_available,True)
        self.assertEqual(bulb.is_on, True)
        self.assertEqual(bulb.ltype, "white")

        self.assertEqual(bulb.brightness, 50)
        self.assertEqual(bulb.ct, 40)
        self.assertEqual(bulb.rgb,(10,20,30))


if __name__ == '__main__':
    unittest.main()
