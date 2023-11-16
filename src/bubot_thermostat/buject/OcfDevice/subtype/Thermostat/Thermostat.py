import asyncio
from bubot_thermostat_sml1000 import __version__ as device_version
from bubot.buject.OcfDevice.subtype.Device.Device import Device
from .OicRSwitchBinary import OicRSwitchBinary
from bubot.core.ResourceLink import ResourceLink
from bubot_helpers.ExtException import ExtException, ExtTimeoutError, KeyNotFound
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)


class Thermostat(Device):
    version = device_version
    file = __file__

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.temperature_link: ResourceLink = None
        self.actuator_link: ResourceLink = None
        self.resource_layer.add_handler(f'/power', OicRSwitchBinary)

    async def on_pending(self):
        try:
            self.temperature_link, temperature_response = await self.check_link('/oic/con', 'temperatureResURI')
            self.actuator_link, actuator_response = await self.check_link('/oic/con', 'actuatorResURI')
            if self.temperature_link and self.actuator_link:
                await super().on_pending()
            await asyncio.sleep(10)
        except Exception as err:
            raise ExtException(parent=err, action='ModbusSlave.on_pending')

    async def on_idle(self):
        try:
            await self.update_external_links()
            await self.calculate()
        except Exception as err:
            ext_err = ExtException(parent=err)
            self.log.error(ext_err)
            await self.return_to_pending(ext_err)
        pass

    async def update_external_links(self):
        try:
            temperature_resp = await self.temperature_link.retrieve(self)
            self.set_param('/temperature', 'temperature', temperature_resp.get('temperature'))
            self.set_param('/temperature', 'unit', temperature_resp.get('unit'))
        except Exception as err:
            raise ExtException(parent=err, message='Error retrieve temperature')

        try:
            actuator_resp = await self.actuator_link.retrieve(self)
            self.set_param('/actuator', 'value', actuator_resp.get('value'))
        except Exception as err:
            raise ExtException(parent=err, message='Error retrieve actuator')

    async def calculate(self):
        actuator_state = self.get_param('/actuator', 'value')
        desired_temperature = self.get_param('/desired_temperature', 'temperature')
        temperature = self.get_param('/temperature', 'temperature')
        if desired_temperature + 0.2 < temperature and actuator_state:
            print(f'{datetime.now()} {temperature} actuator off')
            await self.actuator_link.update(self, {'value': False})
        elif desired_temperature - 0.2 > temperature and not actuator_state:
            print(f'{datetime.now()} {temperature} actuator on')
            await self.actuator_link.update(self, {'value': True})
