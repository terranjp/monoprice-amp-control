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
        self._setup_serial()

        self.power = None
        self.volume = None
        self.treble = None
        self.balance = None
        self.mute = None
        self.bass = None
        self.source = None
        self.keypad_status = None
        self.DT_status = None
        self.PA_control = None

        self.update_status()

    def __str__(self):

        status_string = "Zone: {}; " \
                        "Name: {}; " \
                        "Power: {}; " \
                        "Mute: {}; " \
                        "Volume: {}; " \
                        "Source: {}; " \
                        "Bass: {}; " \
                        "Treble: {};" \
                        "Balance; {}; " \
                        "Keypad: {};".format(self.zone,
                                             self.name,
                                             self.power,
                                             self.mute,
                                             self.volume,
                                             self.source,
                                             self.bass,
                                             self.treble,
                                             self.balance,
                                             self.keypad_status)

        return status_string

    def _setup_serial(self):
        self.ser = serial.Serial()
        self.ser.port = self.port
        self.ser.baudrate = self.baudrate
        self.ser.timeout = 1

    def _send_command(self, command):
        self.ser.open()
        self.ser.write(command)
        self.ser.close()

    def _query_zone(self):
        self.ser.open()
        command = '?1%s\n\r' % self.zone
        self.ser.write(command)
        response = self.ser.read(30)
        self.ser.close()

        return response

    def set_power(self, power_setting):

        if power_setting is True or power_setting.lower() == 'on':
            command = '<1%sPR%s\r\n' % (self.zone, '01')
            self._send_command(command)

        elif power_setting is False or power_setting.lower() == 'off':
            command = '<1%sPR%s\r\n' % (self.zone, '00')
            self._send_command(command)

    def set_volume(self, new_volume):

        if new_volume > 38:
            new_volume = 38
        elif new_volume < 0:
            new_volume = 0

        if new_volume < 10:
            vol = "0" + str(new_volume)

        command = '<1%sVO%s\r\n' % (self.zone, new_volume)

        self._send_command(command)

    def set_source(self, new_source):
        print(new_source)

        if 1 > int(new_source) < 6:
            raise ValueError("Source must be between 1 and 6")
        else:
            command = '<1%sCH0%s\r\n' % (self.zone, new_source)
            
            self._send_command(command)

    def update_status(self):
        response = self._query_zone()
        parsed_response = self._parse_response(response)
        self._set_status(parsed_response)

    def _set_status(self, parsed_response):

        res = parsed_response

        if res['power_control'] == "01":
            self.power = 'ON'
        elif res['power_control'] == "00":
            self.power = 'OFF'

        if res['PA_control'] == "01":
            self.PA_control = 'ON'
        elif res['PA_control'] == "00":
            self.PA_control = 'OFF'

        if res['mute'] == "01":
            self.mute = "ON"
        elif res['mute'] == "00":
            self.mute = "OFF"

        if res['DT_status'] == "01":
            self.DT_status = "ON"
        elif res['DT_status'] == "00":
            self.DT_status = "OFF"

        if res['keypad_status'] == "01":
            self.keypad_status = "CONNECTED"
        elif res['keypad_status'] == "00":
            self.keypad_status = "DISCONNECTED"

        self.volume = int(res['volume'])
        self.treble = int(res['treble']) - 7
        self.bass = int(res['bass']) - 7
        self.balance = int(res['balance']) - 10
        self.source = int(res['source'])

    @staticmethod
    def _parse_response(response):

        command = response[:4]
        reply = response[7:]

        main_unit = reply[0]
        zone = reply[1]
        PA_control = reply[2:4]
        power_control = reply[4:6]
        mute = reply[6:8]
        DT_status = reply[8:10]
        volume = reply[10:12]
        treble = reply[12:14]
        bass = reply[14:16]
        balance = reply[16:18]
        source = reply[18:20]
        keypad_status = reply[20:22]

        return dict(main_unit=main_unit,
                    zone=zone,
                    PA_control=PA_control,
                    power_control=power_control,
                    mute=mute,
                    DT_status=DT_status,
                    volume=volume,
                    treble=treble,
                    bass=bass,
                    balance=balance,
                    source=source,
                    keypad_status=keypad_status)

zone5 = AmpZone(5)
zone5.update_status()
print(zone5)

zone5.set_source(6)

zone5.update_status()
print(zone5)
