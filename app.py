#!/usr/bin/python3

from flask import Flask, jsonify, abort, make_response
from flask_restful import Api, Resource, reqparse, fields, marshal
from flask_httpauth import HTTPBasicAuth
from flask_cors import CORS, cross_origin

from amp_controller import Amp

app = Flask(__name__, static_url_path="")
CORS(app)
api = Api(app)
auth = HTTPBasicAuth()
amp = Amp()


@auth.get_password
def get_password(username):
    if username == 'tarrenjp':
        return 'james96b'
    return None


@auth.error_handler
def unauthorized():
    # return 403 instead of 401 to prevent browsers from displaying the default
    # auth dialog
    return make_response(jsonify({'message': 'Unauthorized access'}), 403)

amp_zones = amp.get_status()
amp_fields = {
    'unit': fields.Integer,
    'zone': fields.Integer,
    'volume': fields.Integer,
    'power': fields.Boolean,
    'source': fields.Integer,
    'PA': fields.Boolean,
    'DT': fields.Boolean,
    'treble': fields.Integer,
    'bass': fields.Integer,
    'balance': fields.Integer,
    'keypad': fields.Boolean,
    'uri': fields.Url('zone')
}


class AmpAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        super(AmpAPI, self).__init__()

    def get(self):

        amp_zones = amp.get_status()

        return {'zones': [marshal(zone, amp_fields) for zone in amp_zones]}


class AmpZoneAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('volume', type=int, location='json')
        self.reqparse.add_argument('power', type=bool, location='json')
        self.reqparse.add_argument('source', type=str, location='json')
        self.reqparse.add_argument('treble', type=int, location='json')
        self.reqparse.add_argument('bass', type=int, location='json')
        self.reqparse.add_argument('mute', type=bool, location='json')

        super(AmpZoneAPI, self).__init__()

    def get(self, zone):
        zone_status = [status for status in amp_zones if status['zone'] == zone]
        if len(zone_status) == 0:
            abort(404)

        return {'zone': marshal(zone_status[0], amp_fields)}

    def put(self, zone):
        zone_status = [status for status in amp_zones if status['zone'] == zone]

        if len(zone_status) == 0:
            abort(404)

        args = self.reqparse.parse_args()

        for key, value in args.items():

            if key == 'power':
                amp.set_zone_power(zone, value)

            if key == 'volume':
                amp.set_zone_volume(zone, value)

            if key == 'source':
                amp.set_zone_source(zone, value)

            if key == 'bass':
                amp.set_zone_bass(zone, value)

            if key == 'treble':
                amp.set_zone_treble(zone, value)

            if key == 'mute':
                pass

            # zone_status[key] = value

        return args


api.add_resource(AmpAPI, '/amp', endpoint='amp_zones')
api.add_resource(AmpZoneAPI, '/amp/zone/<int:zone>', endpoint='zone')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
