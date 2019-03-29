import random
import struct
import uuid
import requests

def get_mac_address():
    mac_bin_list = []
    mac_hex_list = []
    for i in range(1,7):
        i = random.randint(0x00, 0xff)
        mac_bin_list.append(i)
    Fake_HW = struct.pack("BBBBBB", mac_bin_list[0],mac_bin_list[1], mac_bin_list[2], mac_bin_list[3], mac_bin_list[4], mac_bin_list[5])
    for j in mac_bin_list:
        mac_hex_list.append(hex(j))
    Hardware = ":".join(mac_hex_list).replace("0x","")
    return Hardware

def get_uuid():
    return str(uuid.uuid1())

def get_hostname():
    for idc in ["yz", "zw", "jxq", "tj", "ct"]:
        for bus in ["fang", "zp", "sec", "service", "pay"]:
            for ser in ["web", "wap", "app", "api"]:
                for i in range(1,10):
                    index = "{:0>2}".format(i)
                    hostname = "{}-{}-{}-{}".format(idc,bus,ser,index)
                    yield hostname
def get_ip_address():
    ip_ = "192.168"
    for ip3 in range(1,254,3):
        for ip4 in range(1,254,2):
            ip = "{}.{}.{}".format(ip_,ip3,ip4)
            yield ip

def run():
    hostname = get_hostname()
    ip = get_ip_address()
    data = {}
    data['server_disk'] = "9"
    data['server_type'] = 'kvm'
    data['server_cpu'] = "Intel(R) Core(TM) i5-4278u CPU @ 2.60GHZ 1"
    data['vm_status'] = 1
    data['manufacturers'] = "innotek GmbH"
    data['server_mem'] = '500 MB'
    data['manufacture_date'] = '2012-1-1'
    data['os'] = 'CentOS 6.4 Final'
    data['sn'] = 0
    for i in range(1,800):
        data['uuid'] = get_uuid()
        data['hostname'] = hostname.__next__()
        data['mac_address'] = get_mac_address()
        data['inner_ip'] = ip.__next__()
        send(data)
def send(data):
    url = 'http://192.168.1.10:8000/resources/server/report/'
    r = requests.post(url, data=data)

if __name__ == '__main__':
    run()
