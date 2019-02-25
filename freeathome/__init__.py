''' Main Home Assistant interface Free@Home '''
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.const import (CONF_HOST, CONF_PASSWORD, CONF_PORT,
                                 CONF_USERNAME)
from homeassistant.helpers.discovery import load_platform

from .const import (CONF_USE_ROOM_NAMES, DATA_MFH, DEFAULT_USE_ROOM_NAMES,
                    DOMAIN)
from .pfreeathome import FreeAtHomeSysAp

REQUIREMENTS = ['slixmpp==1.4.2']

# Validation of the user's configuration
CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_HOST): cv.string,
        vol.Optional(CONF_PORT, default=5222): cv.port,
        vol.Optional(CONF_USERNAME, default='admin'): cv.string,
        vol.Optional(CONF_PASSWORD): cv.string,
        vol.Optional(CONF_USE_ROOM_NAMES,
                     default=DEFAULT_USE_ROOM_NAMES): cv.boolean,
    })
}, extra=vol.ALLOW_EXTRA)


async def async_setup(hass, base_config):
    """ Setup of the Free@Home interface for Home Assistant ."""
    config = base_config.get(DOMAIN)

    host = config.get(CONF_HOST)
    port = config.get(CONF_PORT)
    username = config.get(CONF_USERNAME)
    password = config.get(CONF_PASSWORD)

    sysap = FreeAtHomeSysAp(host, port, username, password)
    sysap.use_room_names = config.get(CONF_USE_ROOM_NAMES)
    sysap.connect()

    hass.data[DATA_MFH] = sysap

    resp = await sysap.wait_for_connection()

    if resp:
        await sysap.find_devices()

        load_platform(hass, 'light', DOMAIN, {}, config)
        load_platform(hass, 'scene', DOMAIN, {}, config)
        load_platform(hass, 'cover', DOMAIN, {}, config)
        load_platform(hass, 'binary_sensor', DOMAIN, {}, config)
        load_platform(hass, 'climate', DOMAIN, {}, config)

        return True

    return False
