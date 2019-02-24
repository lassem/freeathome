""" Support for Free@Home thermostats """

import logging
from homeassistant.components.climate import (
    PLATFORM_SCHEMA, ClimateDevice)
from homeassistant.components.climate.const import (
    SUPPORT_OPERATION_MODE, SUPPORT_TARGET_TEMPERATURE,
    SUPPORT_ON_OFF, STATE_ECO, STATE_AUTO)
from homeassistant.const import (
    ATTR_TEMPERATURE, TEMP_CELSIUS, DEVICE_CLASS_TEMPERATURE, STATE_ON, STATE_OFF)

import custom_components.freeathome as freeathome

REQUIREMENTS = ['slixmpp==1.4.2']

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config, add_devices, discovery_info=None):
    """ thermostat specific code."""
    import custom_components.freeathome.pfreeathome

    _LOGGER.info('FreeAtHome setup thermostat')

    fah = hass.data[freeathome.DATA_MFH]

    devices = fah.get_devices('thermostat')

    for device, device_object in devices.items():
        add_devices([FreeAtHomeThermostat(device_object)])


class FreeAtHomeThermostat(ClimateDevice):
    ''' Free@home thermostat '''
    thermostat_device = None
    _name = ''
    _state = None
    _current_operation = None

    def __init__(self, device):
        self.thermostat_device = device
        self._name = self.thermostat_device.name
        self._state = self.thermostat_device.state

    @property
    def name(self):
        """Return the display name of this thermostat."""
        return self._name

    @property
    def unique_id(self):
        """Return the ID """
        return self.thermostat_device.device_id

    @property
    def should_poll(self):
        """Thermostat should be polled"""
        return True

    @property
    def current_temperature(self):
        """Return the current temperature."""
        if self.current_operation == STATE_OFF:
            return None
        return float(self.thermostat_device.current_temperature)

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        return float(self.thermostat_device.target_temperature)

    @property
    def temperature_unit(self):
        """Return the unit of measurement used by the platform."""
        return TEMP_CELSIUS

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return SUPPORT_TARGET_TEMPERATURE | SUPPORT_OPERATION_MODE | SUPPORT_ON_OFF

    @property
    def operation_list(self):
        """Return the list of available operation modes."""
        return [STATE_ECO, STATE_AUTO]

    @property
    def current_operation(self):
        """Return current operation ie. heat, cool, idle."""
        return self._current_operation

    @property
    def icon(self):
        return 'mdi:thermometer-lines'

    async def async_turn_off(self):
        """Turn device off."""
        await self.thermostat_device.turn_off()
        self._current_operation = STATE_OFF

    async def async_turn_on(self):
        """Turn device on."""
        await self.thermostat_device.turn_on()
        self._current_operation = STATE_ON

    async def async_set_operation_mode(self, operation_mode):
        """Set new target operation mode."""
        if operation_mode == STATE_ECO:
            await self.thermostat_device.eco_mode()

        if operation_mode == STATE_AUTO:
            await self.thermostat_device.turn_on()

        self._current_operation = operation_mode

    async def async_set_temperature(self, **kwargs):
        """Set new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        await self.thermostat_device.set_target_temperature(temperature)
