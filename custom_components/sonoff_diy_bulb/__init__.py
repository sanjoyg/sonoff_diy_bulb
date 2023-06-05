"""Sonoff BL05 DIY Mode Integration"""
from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry, ConfigEntryState

import logging

logger = logging.getLogger("sonoff-diy-bulb-adapter")

def setup(hass: HomeAssistant, config: ConfigType) -> bool:
    logger.debug("In init setup...")
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    logger.debug("async_setup_entry in __init__ start...")
    logger.debug(entry.version)
    logger.debug(entry.domain)
    logger.debug(entry.title)
    logger.debug(entry.data)
    logger.debug(entry.source)
    logger.debug(entry.unique_id)
    logger.debug(entry.entry_id)
    logger.debug(entry.state)

    hass.async_create_task(hass.config_entries.async_forward_entry_setup(entry, "light"))
    return True

async def async_update_options(hass: HomeAssistant, entry: ConfigEntry):
    logger.debug("in async_update_options...")
    await hass.config_entries.async_reload(entry.entry_id)