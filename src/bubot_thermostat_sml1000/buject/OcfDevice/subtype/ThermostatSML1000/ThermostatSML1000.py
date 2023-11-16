from bubot_modbus.buject.OcfDevice.subtype.ModbusSlave.ModbusSlave import ModbusSlave
from bubot_thermostat_sml1000 import __version__ as device_version
from .lib.ThermostatSML1000 import ThermostatSML1000 as ModbusDevice
from .ResPower import ResPower
from .ResTemperatureExternal import ResTemperatureExternal
from .ResTemperatureInternal import ResTemperatureInternal
# import logging

# _logger = logging.getLogger(__name__)


class ThermostatSML1000(ModbusSlave):
    ModbusDevice = ModbusDevice
    version = device_version
    file = __file__

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.resource_layer.add_handler(f'/power', ResPower)
        self.resource_layer.add_handler(f'/temperature/internal', ResTemperatureInternal)
        self.resource_layer.add_handler(f'/temperature/external', ResTemperatureExternal)

    async def retrieve_power(self):
        res = await self.modbus.read_param('power')
        self.set_param('/power', 'value', res)
        return res

    async def retrieve_temperature_internal(self):
        res = await self.modbus.read_param('temperature_internal')
        self.set_param('/temperature/internal', 'temperature', res)
        return self.get_param('/temperature/internal')

    async def retrieve_temperature_external(self):
        res = await self.modbus.read_param('temperature_external')
        self.set_param('/temperature/external', 'temperature', res)
        return self.get_param('/temperature/external')

    async def update_power(self, value):
        if value is not None:
            await self.modbus.write_param('power', value)
        self.set_param('/power', value, value)

    async def on_idle(self):
        try:
            await self.retrieve_power()
        except Exception as err:
            self.log.error(err)
