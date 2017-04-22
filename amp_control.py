from __future__ import division

import serial
import time


class AmpZone(object):
    MAX_VOLUME = 38
    MIN_TREBLE = 0
    MAX_TREBLE = 14

    def __init__(self, zone, name=None, port='/dev/ttyUSB0', baudrate=9600):
        self.name = name
        self.zone = zone
        self.port = port
        self.baudrate = baudrate
        self._setupSerialPort()

        self.power = None
        self.volume = None
        self.treble = None
        self.balance = None
        self.mute = None
        self.bass = None
        self.source = None

        # response = self.get_zone_status()
        # self.parse_response(response)

    def _setupSerialPort(self):
        self.ser = serial.Serial()
        self.ser.port = self.port
        self.ser.baudrate = self.baudrate
        self.ser.timeout = 1

    def send_comand(self, command):
        self.ser.open()
        self.ser.write(command)
        time.sleep(0.1)
        response = self.ser.read(30)
        self.ser.close()

    def get_zone_status(self):
        self.ser.open()
        command = '?1%s\n\r' % self.zone

        self.ser.write(command)
        time.sleep(0.1)
        response = self.ser.read(30)
        self.ser.close()

        return response

    @property
    def src(self):
        response = self.get_zone_status()
        return response[25:27]

    @src.setter
    def src(self, new_source):
        command = '<1%sCH%s\r\n' % (self.zone, new_source)
        self.send_comand(command)


    @property
    def pwr(self):
        response = self.get_zone_status()

        if response[11:13] == "01":
            return "ON"
        elif response[11:13] == "00":
            return "OFF"

    @pwr.setter
    def pwr(self, power_setting):
        if power_setting is True or power_setting.lower() == 'on':
            command = '<1%sPR%s\r\n' % (self.zone, '01')
            self.send_comand(command)

        elif power_setting is False or power_setting.lower() == 'off':
            command = '<1%sPR%s\r\n' % (self.zone, '00')
            self.send_comand(command)

    @property
    def vol(self):
        response = self.get_zone_status()
        response_vol = int(response[17:19])

        return response_vol

    @vol.setter
    def vol(self, new_volume):
        if new_volume > 38:
            new_volume = 38
        elif new_volume < 0:
            new_volume = 0

        if new_volume < 10:
            new_volume = "0" + str(new_volume)

        command = '<1%sVO%s\r\n' % (self.zone, new_volume)

        self.send_comand(command)

    def set_power(self, power_setting):

        if power_setting is True or power_setting.lower() == 'on':
            command = '<1%sPR%s\r\n' % (self.zone, '01')
            self.send_comand(command)

        elif power_setting is False or power_setting.lower() == 'off':
            command = '<1%sPR%s\r\n' % (self.zone, '00')
            self.send_comand(command)

    def set_volume(self, new_volume):

        if new_volume > 38:
            new_volume = 38
        elif new_volume < 0:
            new_volume = 0
        #
        # vol = int(new_volume * self.MAX_VOLUME / 100)
        #
        if new_volume < 10:
            vol = "0" + str(new_volume)

        command = '<1%sVO%s\r\n' % (self.zone, new_volume)

        self.send_comand(command)

    def set_source(self, new_source):

        command = '<1%sCH%s\r\n' % (self.zone, new_source)
        self.send_comand(command)

    def parse_response(self, response):

        if response[11:13] == "01":
            self.power = "ON"
        elif response[11:13] == "00":
            self.power = "OFF"

        if response[13:15] == "01":
            self.mute = "ON"
        elif response[13:15] == "00":
            self.mute = "OFF"

        if response[15:17] == "01":
            DT_status = "ON"
        elif response[15:17] == "00":
            DT_status = "OFF"

        self.volume = response[17:19]
        self.treble = response[19:21]
        self.bass = response[21:23]
        self.balance = response[23:25]
        self.source = response[25:27]

zone6 = AmpZone(6)
zone6.pwr = True
zone6.src = '04'

print(zone6.src)
