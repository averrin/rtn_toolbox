from __future__ import print_function
import datetime
import json


def encodeInt(number):
    encoded = []
    number = int(number)
    while number > 127:
        encoded.append(int(number & 0xFF | 0x80))
        number = round(int(number / (2 ** 7)))
    encoded.append(int(number) & 0xFF)
    return ''.join(map(chr, encoded))


class Decoder(object):

    def __init__(self, msg):
        msg = msg.replace(' ', '')
        self.data = [msg[i:i + 2] for i in range(0, len(msg), 2)]
        self.cursor = 0
        self.message = {}

    def decode(self):
        dncs = ''
        for i in xrange(0, 3):
            dncs += str(int(self.data[self.cursor], 16))
            dncs += '.'
            self.cursor += 1
        dncs += str(int(self.data[self.cursor], 16))
        self.message['dncs'] = dncs
        self.cursor += 1

        self.message['hubid'] = self.read7bit()
        self.message['version'] = self.read7bit()
        self.message['services_count'] = self.read7bit()

        self.message['services'] = []
        if self.message['services_count']:
            for i in xrange(self.message['services_count']):
                s = self.readString()
                self.message['services'].append(s)

        self.message['callsigns_count'] = self.read7bit()
        self.message['callsigns'] = []
        if self.message['callsigns_count']:
            for i in xrange(self.message['callsigns_count']):
                cs = self.readString()
                self.message['callsigns'].append(cs)

        while self.cursor != len(self.data) - 1:
            self.message['package_type'] = self.read7bit()
            self.message['study_code'] = self.read7bit()
            ts = "".join(self.data[self.cursor:self.cursor + 4])
            self.message['start_timestamp'] = int(ts, 16)
            self.message['start_timestamp_formatted'] = datetime.datetime.fromtimestamp(
                self.message['start_timestamp'])
            self.cursor += 4
            self.message['events_number'] = self.read7bit()
            self.message['events'] = []
            for i in xrange(self.message['events_number']):
                td = self.read7bit()
                eid = self.read7bit()
                event = self.readEvent(eid, td)
                self.message['events'].append(event)
            break
        return self.message

    def read7bit(self):
        parameter = 0
        isn = 0
        i = 0
        for n in xrange(self.cursor, len(self.data)):
            parameter += int(self.data[n], 16) << (7 * i)
            isn = int(self.data[n], 16) >> 7
            if isn:
                parameter -= 1 << (7 * (i + 1))
                i += 1
            else:
                i += 1
                break
        self.cursor += i
        return parameter

    def readString(self):
        s = ''
        l = self.read7bit()
        i = 0
        for i in xrange(self.cursor, self.cursor + l):
            s += chr(int(self.data[i], 16))
        self.cursor = i + 1
        return s

    def readEvent(self, id, td):
        print(id)
        event = {"id": id, 'timedelta': td}
        if id == 8:
            event['type'] = 'channel tune'
            event['sessions'] = []
            event['channel'] = self.read7bit()
            cs = self.read7bit()
            event['callsign'] = self.message['callsigns'][cs]
            ls = self.read7bit()
            for i in xrange(ls):
                tt = self.read7bit()
                d = self.read7bit()
                event['sessions'].append({"tune_time": tt, "duration": d})
        elif id == 0:
            event['type'] = 'mosaic session'
            cs = self.read7bit()
            event['callsign'] = self.message['callsigns'][cs]
            event["duration"] = self.read7bit()
            event['exit_type'] = chr(self.read7bit())
            event['exit_value'] = self.read7bit()
            event['banner_code'] = self.read7bit()
        elif id == 1:
            event['type'] = 'ace/upsell menu item enter'
            event["menu_id"] = self.read7bit()
            event["duration"] = self.read7bit()
            event['exit_type'] = chr(self.read7bit())
            event['exit_value'] = self.read7bit()
            event['banner_code'] = self.read7bit()
        elif id == 2:
            event['type'] = 'banner impression'
            event["source"] = self.read7bit()
            event["banner_id"] = self.read7bit()
            event['duration'] = self.read7bit()
            event['activated'] = self.read7bit()
        elif id == 3:
            event['type'] = 'upsell order now'
            event["menu_id"] = self.read7bit()
        elif id == 4:
            event['type'] = 'EBIF app session'
            event["app"] = self.read7bit()
            event["duration"] = self.read7bit()
        elif id == 5:
            event['type'] = 'searches count'
            event["count"] = self.read7bit()
            event["filters"] = self.read7bit()
        elif id == 6:
            event['type'] = 'search option activation'
            event["search_element_code"] = self.read7bit()
            event["duration"] = self.read7bit()
            event['exit_type'] = chr(self.read7bit())
            event['exit_value'] = self.read7bit()
        elif id == 7:
            event['type'] = 'upsell from search'
            event["purchaseValue"] = self.read7bit()
        elif id == 9:
            event['type'] = 'VOD Playing/Ordering'
            event["vod_action"] = self.read7bit()
            event["vod_asset_id"] = self.read7bit()
            event['vod_context_id'] = self.read7bit()
        elif id == 10:
            event['type'] = 'Upsell impressions'
            event["screen_id"] = self.read7bit()
            event["entry_point"] = self.read7bit()
            event["exit_point"] = self.read7bit()
        elif id == 11:
            event['type'] = 'Upsell sessions'
            event["count"] = self.read7bit()
            event["duration"] = self.read7bit()
        elif id == 12:
            event['type'] = 'Upsell purchases'
            event["purchase_value"] = self.readString()
            event["discount"] = self.readString()
            event["putchase_type"] = self.read7bit()
        else:
            return event
            # raise Exception("Event type not implemented")
        return event

    def display(self, show=print):
        m = self.message
        show("dncs: %(dncs)s" % m)
        show("hubid: %(hubid)s" % m)
        show("ver: %(version)s" % m)
        show("launched services count: %(services_count)s" % m)
        if m['services']:
            show("services: %s" % ", ".join(m['services']))

        show("used callsigns count: %(callsigns_count)s" % m)
        if m['callsigns']:
            show("callsigns: %s" % ", ".join(m['callsigns']))

        show('package type: %(package_type)s' % m)
        show('study code: %(study_code)s' % m)
        show("start_timestamp: %(start_timestamp_formatted)s" % m)
        show('events count: %(events_number)s' % m)
        if m['events_number']:
            show('events:')
            for e in m['events']:
                show(json.dumps(e, indent=4))

    def json(self, indent=4):
        msg = self.message.copy()
        msg['start_timestamp_formatted'] = str(
            msg['start_timestamp_formatted'])
        return json.dumps(msg, indent=indent)

if __name__ == '__main__':
    import sys
    decoder = Decoder(sys.argv[1])
    decoder.decode()
    decoder.display()
