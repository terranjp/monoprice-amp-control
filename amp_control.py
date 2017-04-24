#!/usr/bin/python3

import serial


class Amp(object):
    MAX_VOLUME = 38
    MIN_TREBLE = 0
    MAX_TREBLE = 14

    def __init__(self, port='/dev/ttyUSB0', baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        self.ser = None
        self._setup_serial()

        self.status = None

        self.update_status()

    def __str__(self):

        return str(self.status)

    def _setup_serial(self):
        self.ser = serial.Serial()
        self.ser.port = self.port
        self.ser.baudrate = self.baudrate
        self.ser.timeout = 1

    def _send_command(self, command):
        self.ser.open()
        self.ser.write(command.encode('utf-8'))
        self.ser.close()

    def query_zone(self, zone):
        self.ser.open()
        command = '?1%s\n\r' % zone
        self.ser.write(command)
        response = self.ser.read(30)
        self.ser.close()

        return response

    def set_zone_power(self, zone, power_setting):

        if power_setting is True:
            command = '<1%sPR0%s\r\n' % (zone, '1')
            self._send_command(command)

        elif power_setting is False:
            command = '<1%sPR0%s\r\n' % (zone, '0')
            self._send_command(command)

    def set_zone_mute(self, zone, mute_setting):

        if mute_setting is True:
            command = '<1%sMU0%s\r\n' % (zone, '1')
            self._send_command(command)

        elif mute_setting is False:
            command = '<1%sMU0%s\r\n' % (zone, '0')
            self._send_command(command)

    def set_zone_volume(self, zone, new_volume):

        if new_volume > 38:
            new_volume = 38
        elif new_volume < 0:
            new_volume = 0

        if new_volume < 10:
            new_volume = "0" + str(new_volume)

        command = '<1%sVO%s\r\n' % (zone, new_volume)

        self._send_command(command)

    def set_zone_source(self, zone, new_source):

        if 1 > int(new_source) < 6:
            raise ValueError("Source must be between 1 and 6")
        else:
            command = '<1%sCH0%s\r\n' % (zone, new_source)

            self._send_command(command)

    def set_zone_bass(self, zone, new_bass):

        if new_bass > 7:
            new_bass = 7
        elif new_bass < -7:
            new_bass = -7

        new_bass = new_bass + 7

        if new_bass < 10:
            new_bass = "0" + str(new_bass)

        command = '<1%sBS%s\r\n' % (zone, new_bass)
        self._send_command(command)

    def set_zone_treble(self, zone, new_treble):

        if new_treble > 7:
            new_treble = 7
        elif new_treble < -7:
            new_treble = -7

        new_treble = new_treble + 7

        if new_treble < 10:
            new_treble = "0" + str(new_treble)

        command = '<1%sTR%s\r\n' % (zone, new_treble)
        self._send_command(command)

    def update_status(self):
        responses = self._query_zones()
        parsed_responses = self._parse_responses(responses)

        self.status = parsed_responses

    def get_status(self):

        responses = self._query_zones()
        parsed_responses = self._parse_responses(responses)

        return parsed_responses

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

    def _query_zones(self):
        zones = [1, 2, 3, 4, 5, 6]

        self.ser.open()
        responses = []

        for zone in zones:
            command = '?1%s\n\r' % zone
            self.ser.write(command.encode('utf-8'))
            cmd = self.ser.readline()
            res = self.ser.readline()
            responses.append(res.decode('utf-8'))

        self.ser.close()

        return responses

    @staticmethod
    def _parse_responses(responses):

        parsed_responses = []

        for res in responses:

            res = res[2:]

            unit = int(res[0])
            zone = int(res[1])
            PA = int(res[2:4])
            power = int(res[4:6])
            mute = int(res[6:8])
            DT = int(res[8:10])
            volume = int(res[10:12])
            treble = int(res[12:14])
            bass = int(res[14:16])
            balance = int(res[16:18])
            source = int(res[18:20])
            keypad = int(res[20:22])

            parsed_res = dict(unit=unit,
                              zone=zone,
                              PA=PA,
                              power=power,
                              mute=mute,
                              DT=DT,
                              volume=volume,
                              treble=treble,
                              bass=bass,
                              balance=balance,
                              source=source,
                              keypad=keypad)

            parsed_responses.append(parsed_res)

        return parsed_responses
