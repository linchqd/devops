from django.conf import settings
from resources.models import Server
from monitor.models import ZabbixHosts
from zabbix_client import ZabbixServerProxy
import logging
import json

logger = logging.getLogger(__name__)

class Zabbix(object):
    def __init__(self):
        self.zb = ZabbixServerProxy(settings.ZABBIX_API)
        self.zb.user.login(user=settings.ZABBIX_USER, password=settings.ZABBIX_USERPASS)

    def get_hosts(self):
        return self.zb.host.get(output=["hostid", "host"], selectInterfaces=["ip"])

    def get_groups(self):
        return self.zb.hostgroup.get(output=["groupid", "name"])

    def create_host(self, params):
        return self.zb.host.create(**params)

    def get_templates(self, hostids=None):
        if hostids:
            return self.zb.template.get(output=["name", "templateid"], hostids=hostids)
        return self.zb.template.get(output=["name", "templateid"])

    def link_templates(self, hostid, templateids):
        linked_templates = [tid["templateid"] for tid in self.get_templates(hostid)]
        linked_templates.extend(templateids)
        templates = []
        for tid in linked_templates:
            templates.append({"templateid": tid})
        try:
            return self.zb.host.update(hostid=hostid, templates=templates)
        except Exception as e:
            return e.args

    def unlink_template(self, hostid, templateid):
        try:
            return self.zb.host.update(hostid=hostid, templates_clear=[{"templateid": templateid}])
        except Exception as e:
            raise Exception(e.args)

def process_hosts(zbhosts):
    ret = []
    iplist = []
    for host in zbhosts:
        try:
            ip = host['interfaces'][0]['ip']
        except KeyError as e:
            logger.error("获取ip失败: {}, {}".format(json.dumps(host), e.args))
        else:
            del host['interfaces']
            host['ip'] = ip
            ret.append(host)
            if ip in iplist:
                logger.error("zabbix中存在多条相同ip的设备[{}]".format(ip))
            else:
                iplist.append(ip)
    return ret

def cache_host():
    ZabbixHosts.objects.all().delete()
    zb_hosts = process_hosts(Zabbix().get_hosts())
    for host in zb_hosts:
        try:
            server_obj = Server.objects.get(inner_ip__exact=host['ip'])
        except Server.DoesNotExist:
            logger.error("zabbix监控的设备[{}],CMDB中不存在".format(host['ip']))
        except Server.MultipleObjectsReturned:
            logger.error("zabbix监控的设备[{}],CMDB中存在多条".format(host['ip']))
        else:
            host['server'] = server_obj
            zh_obj = ZabbixHosts(**host)
            try:
                zh_obj.save()
            except Exception as e:
                logger.error("保存zabbix_cache_host失败,{}".format(e.args))

def create_host(serverids = [], group_id = "2"):
    ret_data = []
    if isinstance(serverids, list) and serverids:
        for server in Server.objects.filter(id__in=serverids):
            logger.debug("开始同步服务器: {}".format(server.hostname))
            zb_data = {}
            zb_data["hostname"] = server.hostname
            try:
                logger.debug("zabbix创建主机: {}".format(server.hostname))
                hostid = _create_host(server.hostname, server.inner_ip, group_id)
                zb_data["status"] = True
                logger.debug("zabbix创建主机 {} 成功".format(server.hostname))
            except Exception as e:
                zb_data["status"] = False
                zb_data["errmsgs"] = e.args[0]
                logger.error("zabbix创建主机 {} 失败: {}".format(server.hostname, e.args))
            else:
                try:
                    logger.debug("开始同步缓存表")
                    zb = ZabbixHosts()
                    zb.hostid = hostid
                    zb.host = server.hostname
                    zb.server = server
                    zb.ip = server.inner_ip
                    zb.save()
                    logger.debug("同步缓存表成功")
                except Exception as e:
                    zb_data["status"] = False
                    zb_data["errmsgs"] = "zabbix创建主机成功,同步缓存表失败.{}".format(e.args[1])
                    logger.error("同步缓存表失败.{}".format(e.args))
            ret_data.append(zb_data)
            logger.debug("同步服务器: {} 完成".format(server.hostname))
    return ret_data

def _create_host(hostname, inner_ip, group_id="2", port="10050"):
    data = {
        "host": hostname,
        "interfaces": [
            {
                "type": 1,
                "main": 1,
                "useip": 1,
                "ip": inner_ip,
                "dns": "",
                "port": port,
            }
        ],
        "groups": [
            {
                "groupid": group_id
            }
        ],
    }
    try:
        ret = Zabbix().create_host(data)
        if 'hostids' in ret:
            return ret["hostids"][0]
        else:
            raise Exception(ret["hostids"][0])
    except Exception as e:
        raise Exception(e.args[0])

def get_templates(hostids=None):
    if hostids:
        return Zabbix().get_templates(hostids)
    return Zabbix().get_templates()

def link_templates(hostids, templateids):
    zb = Zabbix()
    data = []
    for serverid in hostids:
        ret_data = {}
        logger.debug("开始为server: {}绑定模版".format(serverid))
        try:
            server = Server.objects.get(pk__exact=serverid)
            hostid = server.zabbixhosts.hostid
            ret_data["hostname"] = server.hostname
            ret = zb.link_templates(hostid, templateids)
        except Server.DoesNotExist:
            ret_data["status"] = 1
            ret_data["msgs"] = "服务器不存在"
            logger.debug("server: {}不存在".format(serverid))
        except AttributeError:
            ret_data["status"] = 1
            ret_data["msgs"] = "服务器没有被监控"
            logger.debug("server: {}没有被监控".format(serverid))
        except Exception as e:
            ret_data["status"] = 1
            ret_data["msgs"] = e.args
            logger.debug("server: {}绑定模版失败，原因:{}".format(serverid, e.args))
        else:
            if "hostids" in ret:
                ret_data["status"] = 0
                logger.debug("server: {}绑定模版成功".format(serverid))
            else:
                ret_data["status"] = 1
                ret_data["msgs"] = ret[0]
                logger.debug("server: {}绑定模版失败，原因:{}".format(serverid, ret[0]))
        data.append(ret_data)
    return data
