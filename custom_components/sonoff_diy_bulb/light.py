import logging
import voluptuous as vol
from pprint import pformat
import homeassistant.helpers.config_validation as cv
#from homeassistant.const import CONF_FILENAME, CONF_HOST
from homeassistant.components.light import PLATFORM_SCHEMA
from homeassistant.const import CONF_DEVICE_ID, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from . import sonoff_bulb

from datetime import timedelta
SCAN_INTERVAL = timedelta(seconds=10)

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_BRIGHTNESS_PCT,
    ATTR_COLOR_TEMP,
    ATTR_COLOR_TEMP_KELVIN,
    ATTR_EFFECT,
    ATTR_FLASH,
    ATTR_RGB_COLOR,
    ATTR_TRANSITION,
    ATTR_WHITE,
    FLASH_LONG,
    FLASH_SHORT,
    ColorMode,
    LightEntity,
    LightEntityFeature
)

logger = logging.getLogger("sonoff-diy-bulb-adapter")

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_NAME): cv.string,
    vol.Required(CONF_DEVICE_ID): cv.string,
    vol.Optional("mock", default=False): cv.boolean
})

from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry, ConfigEntryState

async def async_setup_platform(
        hass : HomeAssistant, 
        config : ConfigType, 
        add_entities : AddEntitiesCallback, 
        discovery_info : DiscoveryInfoType | None = None) -> None:
    logger.info("Setup Platform start...")

    name = config.get(CONF_NAME)
    config_id = config.get(CONF_DEVICE_ID)
    mock = config.get("mock")

    logger.info("Mock Mode: {}".format(mock))
    add_entities([sonoff_diy_bulb(name, config_id, mock)], True)
    logger.info("Setup Platform complete...")

async def async_setup_entry(hass: HomeAssistant, config: ConfigEntry, async_add_entities: AddEntitiesCallback,) -> None:
    
    logger.debug("In here at light with etnry")
    logger.debug(config)
    logger.debug(config.data)
    name = config.data[CONF_NAME]
    config_id = config.data[CONF_DEVICE_ID]
    mock = config.data["mock"]

    logger.info("Mock Mode: {}".format(mock))
    async_add_entities([sonoff_diy_bulb(name, config_id, mock)], True)
    logger.info("Setup Platform complete...")
    
class sonoff_diy_bulb(LightEntity):
    
    def __init__(self, name, device_id, mock=False) -> None:
        logger.debug("sonoff_diy_bulb ctor...")
        self._bulb = sonoff_bulb.sonoff_bulb(name, device_id, mock)

    @property
    def name(self) -> str:
        return self._bulb.name

    @property
    def brightness(self):
        logger.debug("brightness...")
        brightness = self._bulb.brightness
        # Normalize to 255 scale
        brightness = int(2.54 * brightness)
        return brightness

    @property
    def color_temp(self):
        logger.debug("color_temp...")
        return self._bulb.ct
        
    @property
    def is_on(self):
        logger.debug("is_on...")
        return self._bulb.is_on

    @property
    def supported_color_modes(self):
        logger.debug("supported_color_modes...")
        return set([ColorMode.RGB, ColorMode.BRIGHTNESS, ColorMode.WHITE, ColorMode.COLOR_TEMP])

    @property
    def supported_features(self):
        logger.debug("supported_features...")
        return LightEntityFeature.TRANSITION

    def update(self):
        logger.debug("update...")
        self._bulb.set_state()

    def turn_on(self, **kwargs):
        # Notes
        # when turned on only payload is {} , basically no attributes
        # when brightness adjusted only payload is {brightness: value (0-254)}
        # when rgb adjusted only payload is {rgb values: value (0-255)}
        # when white selected only payload is {white: value (0-255)}
        # when temp selected only payload is {color_temp: value , color_temp_kelvin: value }

        logger.debug("turn_on...")
        logger.debug(pformat(kwargs))

        if len(kwargs.keys()) == 0:
            #Just Turn on
            logger.debug("Request to turn on...")
            self._bulb.switch_on()
            return

        if ATTR_WHITE in kwargs:
            # If request is white then brightness is passed
            logger.debug("Request to be white...")
            brightness = int(kwargs[ATTR_WHITE] * 100/254) 
            logger.debug("White brightness : {}".format(brightness))
            self._bulb.set_white(brightness)
            return

        if ATTR_RGB_COLOR in kwargs:
            # If rgb color then only the colors are passed
            logger.debug("Request to be white...")
            rgb = kwargs[ATTR_RGB_COLOR]
            logger.debug("RGB : {}".format(rgb))
            self._bulb.set_rgb(rgb[0], rgb[1], rgb[2])
            return

        if ATTR_BRIGHTNESS in kwargs:
            # brightness requested
            logger.debug("Request to set brightness...")
            brightness = int(kwargs[ATTR_BRIGHTNESS] * 100/254) 
            logger.debug("Set brightness : {}".format(brightness))
            self._bulb.set_brightness(brightness)
            return

        if ATTR_COLOR_TEMP_KELVIN in kwargs:
            # color temp requested
            # If request is white then brightness is passed
            logger.debug("Request to set color temp...")
            ct = kwargs[ATTR_COLOR_TEMP_KELVIN]
            logger.debug("Set CT : {}".format(ct))
            self._bulb.set_ct(ct)
            return

        logger.warning("Could not process any request, shouldnt have reached here...")

    def turn_off(self, **kwargs):
        logger.debug("turn_off...")
        self._bulb.switch_off()
        logger.debug(self._bulb)

    @property
    def state(self):
        logger.debug("state()...")
        logger.debug(self._bulb.is_available)
        if self._bulb.is_available:
            logger.debug("returning {}..".format(self._bulb.is_on))
            return "on" if self._bulb.is_on else "off" 
        logger.debug("returning unavailable..")
        return "unavailable" 

    @property
    def min_mireds(self) -> int:
        return 1

    @property
    def max_mireds(self) -> int:
        return 100

    @property
    def min_color_temp_kelvin(self) -> int:
        return 1

    @property
    def max_color_temp_kelvin(self) -> int:
        return 100
