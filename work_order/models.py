from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class WorkOrder(models.Model):
    ORDER_TYPE = (
        (0, '数据裤'),
        (1, 'web服务'),
        (2, '配置文件'),
        (3, '其他'),
    )
    STAUTS = (
        (0, '申请中'),
        (1, '处理中'),
        (2, '完成'),
        (3, '已取消')
    )
    title          = models.CharField(u'工单标题', max_length=100)
    order_type      = models.IntegerField(u'工单类型', choices=ORDER_TYPE, default=0)
    order_contents  = models.TextField(u'工单内容')
    order_applicant = models.ForeignKey(User, verbose_name=u"申请人", related_name="order_applicant")
    order_assign_to = models.ForeignKey(User, verbose_name=u'指派给那个用户')
    order_status    = models.IntegerField(u'工单状态', choices=STAUTS, default=0)
    order_result    = models.TextField(u'处理结果', null=True, blank=True)
    apply_time      = models.DateTimeField(u'申请时间', auto_now_add=True)
    completed_time  = models.DateTimeField(u'完成时间', auto_now=True)

    def __str__(self):
        return self.title
    class Meta:
        verbose_name = 'work_order'
        db_table = "work_order"
        ordering = ['-completed_time']