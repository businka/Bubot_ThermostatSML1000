import asyncio
import logging
import time
import unittest

from aio_modbus_client.ModbusProtocolRtuHF5111 import ModbusProtocolRtuHF5111 as Protocol
from aio_modbus_client.TransportSocket import TransportSocket as Modbus
from .ThermostatSML1000 import ThermostatSML1000 as Device


class TestThermostatSML1000(unittest.IsolatedAsyncioTestCase):

    @classmethod
    def setUpClass(cls):
        logging.basicConfig(level=logging.DEBUG)
        device_address = 162
        address = ('192.168.1.25', 502)
        cls.device = Device(device_address, Protocol(Modbus(host=address[0], port=address[1])))

    async def asyncTearDown(self):
        await self.device.close()

    async def test_read_power(self):
        power = await self.device.read_param('power')
        print(power)
        pass

    async def test_read(self):
        # self.device.modbus = ModbusTcpChinaGarbage(self.address, framer=ModbusFramer)
        power = await self.device.read_param('power')
        temperature_external = await self.device.read_param('temperature_external')
        temperature_internal = await self.device.read_param('temperature_internal')
        heater = await self.device.read_param('heater')
        temperature_floor = await self.device.read_param('temperature_unknown_2')
        print(f'power: {power}, ext: {temperature_external}, int: {temperature_internal}, heater: {heater}, float: {temperature_floor}')

        pass

    async def test_power(self):
        await self.device.write_param('power', True)
        power = await self.device.read_param('power')
        self.assertEqual(power, True)
        await asyncio.sleep(1)
        await self.device.write_param('power', False)
        power = await self.device.read_param('power')
        self.assertEqual(power, False)
        pass
        # self.assertEqual(100, result)

    async def test_write_time(self):
        value = await self.device.write_param('mode', 1)
        _time = time.localtime()
        minute = await self.device.write_param('minute', _time.tm_min)
        hour = await self.device.write_param('hour', _time.tm_hour)

    async def test_set_temp(self):
        # temp = await self.device.write_param('temperature_external', 30)
        temp = await self.device.write_param('temperature_unknown_2', 30)
        # temperature_unknown_2 = self.device.write_param('temperature_external', 26)
        # temperature_unknown_1 = self.device.write_param('temperature_unknown_1', 25)
        # temperature_unknown_1 = self.device.read_param('temperature_unknown_1')
        # temperature_unknown_2 = self.device.read_param('temperature_unknown_2')

        # print(value)
        # self.assertEqual(value, 'WBMR6C')
        # print(value)

    def test_find(self):
        # self.device.modbus.connect()
        value = self.device.find_devices()
        print(value)

    def test_id_device(self):
        # self.device.modbus.connect()
        self.device.modbus.timeout = 0.5
        value = self.device.is_device()
        self.assertEqual(value, True)
        print(value)

    # def test_pymodbus(self):
    #     slave_id = 0xa3
    #     client = ModbusTcpHF5111('192.168.1.25', framer=ModbusFramer)
    #     result0 = client.read_holding_registers(1, 1, unit=slave_id).registers[0]
    #     result1 = client.write_register(1, 40, unit=slave_id)
    #     print(result0, result1)
    #     pass
    # result1 = client.read_holding_registers(1, 1, unit=self.device_address).registers[0]
    # result2 = client.read_holding_registers(2, 1, unit=self.device_address).registers[0]
    # result3 = client.read_holding_registers(3, 1, unit=self.device_address).registers[0]
    # result4 = client.read_holding_registers(4, 1, unit=self.device_address).registers[0]
    # result5 = client.read_holding_registers(5, 1, unit=self.device_address).registers[0]
    # result6 = client.read_holding_registers(6, 1, unit=self.device_address).registers[0]
    # result7 = client.read_holding_registers(7, 1, unit=self.device_address).registers[0]
    # result8 = client.read_holding_registers(8, 1, unit=self.device_address).registers[0]
    # result = client.read_holding_registers(200, 6, unit=self.device_address)
    # result = client.read_holding_registers(200, 6, unit=self.device_address)
    # print(result.bits[0])
    # client.close()

    # def test_simple(self):
    #     sock = socket.socket()
    #     sock.connect(self.address)
    #     # data = b'\x01\x03\x00\x00\x00\x06\x82\x04\x00\xc8\x00\x06'
    #     # sock.send(data)
    #     # print(sock.recv(1900))
    #     data = b'\x82\x04\x00\xc8\x00\x06\xee\x05'
    #     sock.send(data)
    #     print(sock.recv(1900))
    #     sock.close()
    #     pass
