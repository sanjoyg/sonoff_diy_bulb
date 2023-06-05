import logging
import voluptuous as vol
import socket

import homeassistant.helpers.config_validation as cv
from homeassistant.components.light import PLATFORM_SCHEMA
from homeassistant.const import CONF_DEVICE_ID, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant import data_entry_flow
from homeassistant import config_entries, core
from homeassistant.core import callback

from typing import Any, Dict, Optional

logger = logging.getLogger("sonoff-diy-bulb-config-flow")

DOMAIN="sonoff_diy_bulb"
CONF_MOCK="mock"

DEVICE_SCHEMA = vol.Schema ({
    vol.Required(CONF_NAME): cv.string,
    vol.Required(CONF_DEVICE_ID): cv.string,
    vol.Optional(CONF_MOCK, default=False): cv.boolean
})

import os

def is_sonoff_bulb(device_id, mock):
    logger.info("is_sonoff_bulb for : {}".format(device_id))

    if mock:
        logger.info("Mock bulb, so return True on is_sonoff_bulb...")
        return True

    try:
        url = "http://eWeLink_{}.local".format(device_id)
        logger.info("Will ping to check sonoff device: {}".format(url))
        socket.setdefaulttimeout(1)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((url, 8081))
        s.close()
        logger.debug("Device found successfully....")

    except Exception as error:
        logger.error(error)
        logger.debug("Device not found ....")
        return False

    return True

def validate_name(name):
    logger.debug("validating name : {}".format(name))
    
    if name[0] == ' ' or name[len(name)-1] == ' ':
        return False, "trailing_space"
    logger.debug("name is valid...")
    return True, ""

def validate_device_id(device_id):
    logger.debug("validating device_id : {}".format(device_id))

    import re
    if bool(re.search(r"\s",device_id)):
        return False, "no_space"
    
    logger.debug("device_id is valid...")
    return True, ""

class sonoff_bulb_config_flow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1


    async def async_step_user(self, user_input):
        logger.debug("async_step_user")
        logger.debug("user_input")
    
        errors: Dict[str, str] = {}
        
        if user_input is not None:
            logger.debug("async_step_user user_input is not none...")
            logger.debug(user_input)
            
            valid, key = validate_name(user_input[CONF_NAME])
            
            if not valid:
                logger.debug("Name is invalid, error key : {}".format(key))
                errors["base"] = key
            else:
                valid, key = validate_device_id(user_input[CONF_DEVICE_ID])
                if not valid:
                    logger.debug("device_id is invalid, error key : {}".format(key))
                    errors["base"] = key
                else:
                    if is_sonoff_bulb(user_input[CONF_DEVICE_ID], user_input[CONF_MOCK]):
                        logger.debug("async_step_user sonoff bulb found.. will a create entity...")
                        return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)

                    logger.debug("async_step_user sonoff bulb not found.. will return...")
                    errors["base"] = "not_found"

        logger.debug("async_step_user post user_input not none")
        logger.debug("errors : {}".format(errors))

        return self.async_show_form(step_id="user", data_schema=DEVICE_SCHEMA, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)

class OptionsFlowHandler(config_entries.OptionsFlow):
    
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        logger.debug("options flow handler init...")
        logger.debug(config_entry)
        logger.debug(config_entry.version)
        logger.debug(config_entry.domain)
        logger.debug(config_entry.title)
        logger.debug(config_entry.data)
        logger.debug(config_entry.source)
        logger.debug(config_entry.unique_id)
        logger.debug(config_entry.entry_id)

        self.config_entry = config_entry

    async def async_step_init( self, user_input: Dict[str, Any] = None) -> Dict[str, Any]:
        
        errors: Dict[str, str] = {}

        if user_input is not None:
            logger.debug("async step init user input is not none...")
            logger.debug("user_input is ")
            logger.debug(user_input)
            logger.debug("config_entry is")
            logger.debug(self.config_entry.data)
            
            valid, key = validate_name(user_input[CONF_NAME])
            
            if not valid:
                logger.debug("Name is invalid, error key : {}".format(key))
                errors["base"] = key
            else:
                valid, key = validate_device_id(user_input[CONF_DEVICE_ID])
                if not valid:
                    logger.debug("device_id is invalid, error key : {}".format(key))
                    errors["base"] = key
                else:
                    is_success = True 
                    
                    if self.config_entry.data[CONF_MOCK] != user_input[CONF_MOCK] and not user_input[CONF_MOCK]:
                        # Mock has changed and current value is set to false so check if sonoff
                        if not is_sonoff_bulb(user_input[CONF_MOCK], False):  
                            errors["base"] = "not_found"
                            is_success = False 
                    
                    if is_success:
                        return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)

        options_schema = vol.Schema( {
                vol.Required(CONF_NAME, default=self.config_entry.data[CONF_NAME]): cv.string,
                vol.Required(CONF_DEVICE_ID, default=self.config_entry.data[CONF_DEVICE_ID]): cv.string,
                vol.Optional(CONF_MOCK, default=self.config_entry.data[CONF_MOCK]): cv.boolean, })

        return self.async_show_form(step_id="init", data_schema=options_schema, errors=errors)