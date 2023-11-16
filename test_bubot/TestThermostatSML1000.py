import unittest
from bubot_thermostat_sml1000.buject.OcfDevice.subtype.ThermostatSML1000.ThermostatSML1000 import ThermostatSML1000 as Device
from bubot_modbus.buject.OcfDevice.subtype.SerialServerHF511.SerialServerHF511 import SerialServerHF511 as ModbusDevice
from bubot.core.TestHelper import wait_run_device, wait_cancelled_device, get_config_path
import logging
import asyncio


class TestThermostatSML1000(unittest.TestCase):
    net_interface = "192.168.1.11"
    config = {
        '/oic/con': {
            'master': dict(),
            'slave': 0xa1,
            'baudRate': 9600,
            'parity': 'None',
            'dataBits': 8,
            'stopBits': 1,
            'udpCoapIPv6': None
        }

    }
    modbus_config = {
        '/oic/con': {
            'host': '192.168.1.25',
            'port': 502,
            'baudRate': 9600,
            'parity': 0,
            'dataBits': 8,
            'stopBits': 2,
            'udpCoapIPv4': True,
            'udpCoapIPv6': False
        }
    }

    async def asyncSetUp(self) -> None:
        self.modbus_device = ModbusDevice.init_from_file(di='2')
        self.modbus_task = await wait_run_device(self.modbus_device)
        self.config['/oic/con']['master']['anchor'] = self.modbus_device.link['anchor']
        self.config['/oic/con']['master']['eps'] = self.modbus_device.link['eps']
        self.config['/oic/con']['master']['eps'][0]['net_interface'] = self.net_interface
        self.device = Device.init_from_config(self.config, di='1')
        self.device_task = await wait_run_device(self.device)

    async def asyncTearDown(self) -> None:
        await wait_cancelled_device(self.device, self.device_task)
        await wait_cancelled_device(self.modbus_device, self.modbus_task)

    async def test_update_switch(self):
        value = False
        result1 = (await self.device.retrieve_switch())['value']
        result2 = (await self.device.update_switch(not result1))['value']
        result3 = (await self.device.retrieve_switch())['value']
        self.assertEqual(result3, not result1)
        result4 = (await self.device.update_switch(result1))['value']
        result5 = (await self.device.retrieve_switch())['value']
        self.assertEqual(result5, result1)

    async def test_update_switch(self):
        value = False
        result1 = (await self.device.retrieve_switch())['value']
        result2 = (await self.device.update_switch(not result1))['value']
        result3 = (await self.device.retrieve_switch())['value']
        self.assertEqual(result3, not result1)
        result4 = (await self.device.update_switch(result1))['value']
        result5 = (await self.device.retrieve_switch())['value']
        self.assertEqual(result5, result1)

    @async_test
    async def test_find_devices(self):
        modbus_device = ModbusDevice.init_from_config(self.modbus_config, path=self.config_path)
        mobus_task = await wait_run_device(modbus_device)
        self.config['/oic/con']['master'] = modbus_device.link
        self.device = Device.init_from_config(self.config, path=self.config_path)
        device_task = await wait_run_device(self.device)
        res = await self.device.action_find_devices()
        pass

    @async_test
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

    @async_test
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

    @async_test
    async def test_get_light_baseline(self):
        main = await self.device.run()
        await main
        # while self.device.get_props('/oic/con', 'status_code') == 'load':
        #     await asyncio.sleep(0.1)
        result = await self.device.modbus.read_param('level_blue')
        pass

    @async_test
    def test_get_light1_baseline(self):
        self.device = Device.init_from_config(None, dict(handler=Device.__name__, data=self.config))
        message = OcfRequest(**dict(operation='get', uri='/light'))
        result = self.device.on_get_request(message)
        pass

    @async_test
    def test_set_light_baseline(self):
        self.device = Device.init_from_config(self.config)
        data = dict(value=True, brightness=100)
        message = OcfRequest(**dict(operation='update', uri_path=['light'], data=data))
        self.device.on_init()
        result = self.device.on_post_request(message)
        self.assertDictEqual(result, data)

    @async_test
    def test_get_light_brightness(self):
        self.device = Device.init_from_config(None, dict(handler=Device.__name__, data=self.config))
        message = OcfRequest(**dict(operation='get', uri='/light', query={'rt': ['oic.r.light.brightness']}))
        self.device.on_get_request(message)

        # self.devices.run()
        pass

    @async_test
    async def test_run(self):
        await self.device.run()
        # result = await self.device.coap.discovery_resource()
        await asyncio.sleep(600)
        pass

    @async_test
    async def test_discovery(self):
        await self.device.run()
        result = await self.device.coap.discovery_resource()
        await asyncio.sleep(600)
        pass

    @async_test
    async def test_local_discovery(self):
        msg = OcfRequest(**dict(
            uri_path=['oic', 'res'],
            operation='get'
        ))
        res = self.device.on_get_request(msg)
        await asyncio.sleep(600)
        pass
