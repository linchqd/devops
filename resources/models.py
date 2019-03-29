from django.db import models

# Create your models here.

class Idc(models.Model):
    name = models.CharField(u"机房名称", max_length=20)
    module_letter = models.CharField(u"机房名称简称", max_length=10, db_index=True)
    addr = models.CharField(u"机房地址", max_length=30)
    user_name = models.CharField(u"机房负责人", max_length=10)
    user_phone = models.CharField(u"机房负责人电话", max_length=11)
    user_email = models.EmailField(u"机房负责人邮箱", max_length=20)
    remarks = models.TextField(u"备注", null=True)
    class Meta:
        ordering = ["id"]
        db_table = "resources_idc"
class Server(models.Model):
    manufacturers    = models.CharField(u"制造商", null=True, max_length=64)
    manufacture_date = models.DateField(null=True)
    server_type      = models.CharField(u'服务器类型', max_length=20, null=True)
    sn               = models.CharField(max_length=60, db_index=True, null=True)
    os               = models.CharField(max_length=50, null=True)
    idc              = models.ForeignKey(Idc, null=True)
    hostname         = models.CharField(max_length=50, db_index=True, null=True)
    inner_ip         = models.CharField(max_length=32, unique=True, null=True)
    mac_address      = models.CharField(max_length=50, null=True)
    ip_info          = models.CharField(max_length=255, null=True)
    server_cpu       = models.CharField(max_length=250, null=True)
    server_disk      = models.CharField(max_length=100, null=True)
    server_mem       = models.CharField(max_length=100, null=True)
    status           = models.CharField(max_length=100, null=True)
    remark           = models.TextField(null=True)
    server_id        = models.IntegerField(u'业务线', db_index=True, null=True)
    server_purpose   = models.IntegerField(u'产品线', db_index=True, null=True)
    check_update_time= models.DateTimeField(null=True, auto_now=True)
    vm_status        = models.IntegerField(db_index=True, null=True)
    uuid             = models.CharField(max_length=100, db_index=True, null=True)

    def __str__(self):
        return "{}: ['{}']".format(self.hostname, self.inner_ip)

    class Meta:
        db_table = 'resources_server'
        ordering = ['id']

class Product(models.Model):
    service_name        = models.CharField(u'业务线名称', max_length=50)
    module_letter       = models.CharField(u'业务线名称简称', max_length=10)
    op_interface        = models.CharField(u'运维对接人', max_length=60)
    dev_interface       = models.CharField(u'业务对接人', max_length=60)
    pid                 = models.IntegerField(u'上级业务线id', db_index=True)

    def __str__(self):
        return self.service_name
