import server
import web
import urllib
import json
from datetime import datetime
import time

app = web.application(server.urls, globals())


def make_timestamp(ts):
    d = datetime.strptime(ts, "%Y-%m-%d %H:%M")
    ts = time.mktime(d.timetuple())
    return int(ts)


def values(d, *keys):
    return tuple(map(lambda k: d[k], keys))


def test_simple_request0():
    req = app.request('/details', 'GET')

    assert req.status == "200 OK"
    assert req.headers['Content-Type'] == "application/json"
    data = json.loads(req.data)
    assert data.keys() == ['result']
    assert data['result'].startswith("ERROR")


def test_simple_request8():
    test_ip = '21'
    input_data = {"address": test_ip}
    GET_data = urllib.urlencode(input_data)
    req = app.request('/details?{0}'.format(GET_data), 'GET')

    assert req.status == "200 OK"
    assert req.headers['Content-Type'] == "application/json"
    data = json.loads(req.data)
    assert sorted(data.keys()) == [u'inputs', u'outputs', u'ports', u'unique_in', u'unique_out', u'unique_ports']
    assert values(data, 'unique_in', 'unique_out', 'unique_ports') == (13418L, 3494L, 20371L)
    assert len(data['inputs']['rows']) == 50
    assert len(data['outputs']['rows']) == 50
    assert len(data['ports']['rows']) == 50


def test_simple_request16():
    test_ip = '21.66'
    input_data = {"address": test_ip}
    GET_data = urllib.urlencode(input_data)
    req = app.request('/details?{0}'.format(GET_data), 'GET')

    assert req.status == "200 OK"
    assert req.headers['Content-Type'] == "application/json"
    data = json.loads(req.data)
    assert sorted(data.keys()) == [u'inputs', u'outputs', u'ports', u'unique_in', u'unique_out', u'unique_ports']
    assert values(data, 'unique_in', 'unique_out', 'unique_ports') == (13418L, 3494L, 20371L)
    assert len(data['inputs']['rows']) == 50
    assert len(data['outputs']['rows']) == 50
    assert len(data['ports']['rows']) == 50


def test_simple_request24():
    test_ip = '21.66.10'
    input_data = {"address": test_ip}
    GET_data = urllib.urlencode(input_data)
    req = app.request('/details?{0}'.format(GET_data), 'GET')

    assert req.status == "200 OK"
    assert req.headers['Content-Type'] == "application/json"
    data = json.loads(req.data)
    assert sorted(data.keys()) == [u'inputs', u'outputs', u'ports', u'unique_in', u'unique_out', u'unique_ports']
    assert values(data, 'unique_in', 'unique_out', 'unique_ports') == (2816, 1, 3464)
    assert len(data['inputs']['rows']) == 50
    assert len(data['outputs']['rows']) == 1
    assert len(data['ports']['rows']) == 50


def test_simple_request32():
    test_ip = '21.66.10.70'
    input_data = {"address": test_ip}
    GET_data = urllib.urlencode(input_data)
    req = app.request('/details?{0}'.format(GET_data), 'GET')

    assert req.status == "200 OK"
    assert req.headers['Content-Type'] == "application/json"
    data = json.loads(req.data)
    assert sorted(data.keys()) == [u'inputs', u'outputs', u'ports', u'unique_in', u'unique_out', u'unique_ports']
    assert values(data, 'unique_in', 'unique_out', 'unique_ports') == (30, 0, 30)
    assert len(data['inputs']['rows']) == 50
    assert len(data['outputs']['rows']) == 0
    assert len(data['ports']['rows']) == 30


def test_request_filter():
    test_ip = '21.66.10.70'
    input_data = {"address": test_ip, 'filter': 2}
    GET_data = urllib.urlencode(input_data)
    req = app.request('/details?{0}'.format(GET_data), 'GET')

    assert req.status == "200 OK"
    assert req.headers['Content-Type'] == "application/json"
    data = json.loads(req.data)
    assert sorted(data.keys()) == [u'inputs', u'outputs', u'ports', u'unique_in', u'unique_out', u'unique_ports']
    assert values(data, 'unique_in', 'unique_out', 'unique_ports') == (30, 0, 30)
    assert len(data['inputs']['rows']) == 50
    assert len(data['outputs']['rows']) == 0
    assert len(data['ports']['rows']) == 30


def test_request_timerange():
    time_all = (1, 2 ** 31 - 1)
    time_crop = (make_timestamp('2016-06-21 17:10'), make_timestamp('2016-06-21 18:05'))
    time_tiny = (make_timestamp('2016-06-21 17:45'), make_timestamp('2016-06-21 17:50'))

    test_ip = '21.66.40.231'

    input_data = {"address": test_ip, 'tstart': time_all[0], 'tend': time_all[1]}
    GET_data = urllib.urlencode(input_data)
    req = app.request('/details?{0}'.format(GET_data), 'GET')
    assert req.status == "200 OK"
    assert req.headers['Content-Type'] == "application/json"
    data = json.loads(req.data)
    assert values(data, 'unique_in', 'unique_out', 'unique_ports') == (7, 40, 1)
    assert len(data['inputs']['rows']) == 7
    assert len(data['outputs']['rows']) == 50
    assert len(data['ports']['rows']) == 1

    input_data = {"address": test_ip, 'tstart': time_crop[0], 'tend': time_crop[1]}
    GET_data = urllib.urlencode(input_data)
    req = app.request('/details?{0}'.format(GET_data), 'GET')
    assert req.status == "200 OK"
    assert req.headers['Content-Type'] == "application/json"
    data = json.loads(req.data)
    assert values(data, 'unique_in', 'unique_out', 'unique_ports') == (7, 40, 1)
    assert len(data['inputs']['rows']) == 7
    assert len(data['outputs']['rows']) == 50
    assert len(data['ports']['rows']) == 1

    input_data = {"address": test_ip, 'tstart': time_tiny[0], 'tend': time_tiny[1]}
    GET_data = urllib.urlencode(input_data)
    req = app.request('/details?{0}'.format(GET_data), 'GET')
    assert req.status == "200 OK"
    assert req.headers['Content-Type'] == "application/json"
    data = json.loads(req.data)
    assert values(data, 'unique_in', 'unique_out', 'unique_ports') == (3, 21, 1)
    assert len(data['inputs']['rows']) == 3
    assert len(data['outputs']['rows']) == 34
    assert len(data['ports']['rows']) == 1


def test_request_component():
    for component in ['quick_info', 'inputs', 'outputs', 'ports', 'children', 'summary']:
        req = app.request('/details?address=21.66.40.231&component={0}'.format(component), 'GET')
        assert req.status == "200 OK"
        assert req.headers['Content-Type'] == "application/json"
        data = json.loads(req.data)
        assert data.keys() == [component]
        assert type(data[component]) == dict


def test_multiple_components():
    req = app.request('/details?address=21.66.40.231&component=quick_info,ports,summary', 'GET')
    assert req.status == "200 OK"
    assert req.headers['Content-Type'] == "application/json"
    data = json.loads(req.data)
    keys = sorted(data.keys())
    assert keys == ['ports', 'quick_info', 'summary']
    for k in keys:
        type(data[k]) == dict