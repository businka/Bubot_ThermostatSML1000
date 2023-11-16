import asyncio
import logging
import unittest

from bubot.buject.OcfDevice.subtype.Device.Device import Device
from bubot.core.TestHelper import wait_run_device, wait_cancelled_device

logging.basicConfig()


class TestThermostat(unittest.IsolatedAsyncioTestCase):
    net_interface = "192.168.1.11"
    config = {
        '/desired_temperature': {'temperature': 23.5},
        '/oic/con': {
            # 'sensor': dict(href='/temperature/internal'),
            'temperatureResURI': dict(href='/temperature'),
            'actuatorResURI': dict(href='/v3'),
            'updateTime': 10
        }
    }

    async def asyncSetUp(self) -> None:
        def set_modbus(device):
            device.data['/oic/con']['master']['anchor'] = self.modbus_device.link['anchor']
            device.data['/oic/con']['master']['eps'] = self.modbus_device.link['eps']
            device.data['/oic/con']['master']['eps'][0]['net_interface'] = self.net_interface

        self.modbus_device = Device.init_from_file(di='2', class_name='SerialServerHF511')
        self.modbus_task = await wait_run_device(self.modbus_device)
        self.actuator_device = Device.init_from_file(di='1', class_name='ModbusNonameDAC')
        set_modbus(self.actuator_device)
        self.actuator_task = await wait_run_device(self.actuator_device)

        # self.temperature_device = Device.init_from_file(di='3', class_name='ThermostatSML1000')
        # set_modbus(self.temperature_device)
        self.temperature_device = Device.init_from_file(di='4', class_name='AirQualityMonitorCGDN1')
        self.temperature_task = await wait_run_device(self.temperature_device)

        self.device = Device.init_from_config(self.config, di='7', class_name='Thermostat')
        self.device.data['/oic/con']['temperatureResURI']['anchor'] = self.temperature_device.link['anchor']
        self.device.data['/oic/con']['temperatureResURI']['eps'] = self.temperature_device.link['eps']
        self.device.data['/oic/con']['temperatureResURI']['eps'][0]['net_interface'] = self.net_interface
        self.device.data['/oic/con']['actuatorResURI']['anchor'] = self.actuator_device.link['anchor']
        self.device.data['/oic/con']['actuatorResURI']['eps'] = self.actuator_device.link['eps']
        self.device.data['/oic/con']['actuatorResURI']['eps'][0]['net_interface'] = self.net_interface

        self.task = await wait_run_device(self.device)

        # self.actuator = Device.init_from_config(self.config, di='1')
        # self.device_task = await wait_run_device(self.device)

    async def asyncTearDown(self) -> None:
        print('asyncTearDown')
        await asyncio.gather(
            wait_cancelled_device(self.device, self.task),
            wait_cancelled_device(self.actuator_device, self.actuator_task),
            wait_cancelled_device(self.temperature_device, self.temperature_task),
            wait_cancelled_device(self.modbus_device, self.modbus_task)
        )

    async def test_update_switch(self):
        print('test_update_switch')
        value = False
        await self.task
        # await self.device.update_external_links()

        # result1 = (await self.device.retrieve_switch())['value']
        # result2 = (await self.device.update_switch(not result1))['value']
        # result3 = (await self.device.retrieve_switch())['value']
        # self.assertEqual(result3, not result1)
        # result4 = (await self.device.update_switch(result1))['value']
        # result5 = (await self.device.retrieve_switch())['value']
        # self.assertEqual(result5, result1)

    async def test_find_devices(self):
        modbus_device = ModbusDevice.init_from_config(self.modbus_config, path=self.config_path)
        mobus_task = await wait_run_device(modbus_device)
        self.config['/oic/con']['master'] = modbus_device.link
        self.device = Device.init_from_config(self.config, path=self.config_path)
        device_task = await wait_run_device(self.device)
        res = await self.device.action_find_devices()
        pass

    async def test_is_device(self):
        brightness = 60
        modbus_device = ModbusDevice.init_from_config(self.modbus_config, path=self.config_path)
        mobus_task = await wait_run_device(modbus_device)
        self.config['/oic/con']['master'] = modbus_device.link
        self.device = Device.init_from_config(self.config, path=self.config_path)
        device_task = await wait_run_device(self.device)
        res = await self.device.modbus.is_device()
        self.assertTrue(res)
        pass

    async def test_echo_get_light_baseline(self):
        await self.device.run()
        from aio_modbus_client.ModbusProtocolEcho import ModbusProtocolEcho
        while self.device.get_param('/oic/con', 'status_code') == 'load':
            await asyncio.sleep(0.1)
        self.device.modbus.protocol = ModbusProtocolEcho({
            '\x00\x02\x00\x01': '\x01\x00\x01'
        })
        result = await self.device.modbus.read_param('level_blue')
        pass

    async def test_get_light_baseline(self):
        main = await self.device.run()
        await main
        # while self.device.get_props('/oic/con', 'status_code') == 'load':
        #     await asyncio.sleep(0.1)
        result = await self.device.modbus.read_param('level_blue')
        pass

    def test_get_light1_baseline(self):
        self.device = Device.init_from_config(None, dict(handler=Device.__name__, data=self.config))
        message = OcfRequest(**dict(operation='get', uri='/light'))
        result = self.device.on_get_request(message)
        pass

    def test_set_light_baseline(self):
        self.device = Device.init_from_config(self.config)
        data = dict(value=True, brightness=100)
        message = OcfRequest(**dict(operation='update', uri_path=['light'], data=data))
        self.device.on_init()
        result = self.device.on_post_request(message)
        self.assertDictEqual(result, data)

    def test_get_light_brightness(self):
        self.device = Device.init_from_config(None, dict(handler=Device.__name__, data=self.config))
        message = OcfRequest(**dict(operation='get', uri='/light', query={'rt': ['oic.r.light.brightness']}))
        self.device.on_get_request(message)

        # self.devices.run()
        pass

    async def test_run(self):
        await self.device.run()
        # result = await self.device.coap.discovery_resource()
        await asyncio.sleep(600)
        pass

    async def test_discovery(self):
        await self.device.run()
        result = await self.device.coap.discovery_resource()
        await asyncio.sleep(600)
        pass

    async def test_local_discovery(self):
        msg = OcfRequest(**dict(
            uri_path=['oic', 'res'],
            operation='get'
        ))
        res = self.device.on_get_request(msg)
        await asyncio.sleep(600)
        pass
