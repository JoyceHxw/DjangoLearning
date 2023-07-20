from django.db import models

# Create your models here.
# 用户信息
class UserInfo(models.Model):
    username=models.CharField(verbose_name="用户名",max_length=32)
    password=models.CharField(verbose_name="密码",max_length=32)
    email=models.EmailField(verbose_name="邮箱", max_length=254)
    mobile_phone=models.CharField(verbose_name="手机号", max_length=50)

""" 价格策略 """
class PricePolicy(models.Model):
    category_choices = (
    (1, '免费版'),
    (2, '收费版'),
    (3, '其他'),
    )
    category = models.SmallIntegerField(verbose_name='收费类型', default=2,
    choices=category_choices)
    title = models.CharField(verbose_name='标题', max_length=32)
    # 正整数
    price = models.PositiveIntegerField(verbose_name='价格')
    project_num = models.PositiveIntegerField(verbose_name='项⽬数')
    project_member = models.PositiveIntegerField(verbose_name='项⽬成员数')
    project_space = models.PositiveIntegerField(verbose_name='单项⽬空间',
    help_text='G')
    per_file_size = models.PositiveIntegerField(verbose_name='单⽂件⼤⼩',
    help_text="M")
    # auto_now_add ⾃动将当前时间添加到数据库
    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

""" 交易记录 """
class Transaction(models.Model):
    status_choice = (
    (1, '未⽀付'),
    (2, '已⽀付')
    )
    status = models.SmallIntegerField(verbose_name='状态', choices=status_choice)
    order = models.CharField(verbose_name='订单号', max_length=64, unique=True) # 唯⼀索引
    # 关联⽤户表和价格策略表 外键
    # on_delete=models.CASCADE设置级联删除
    user = models.ForeignKey(verbose_name='⽤户', to='UserInfo', on_delete=models.CASCADE)
    price_policy = models.ForeignKey(verbose_name='价格策略', to='PricePolicy', on_delete=models.CASCADE)
    count = models.IntegerField(verbose_name='数量（年）', help_text='0表示⽆限期')
    price = models.IntegerField(verbose_name='实际⽀付价格')
    start_datetime = models.DateTimeField(verbose_name='开始时间', null=True, blank=True)
    end_datetime = models.DateTimeField(verbose_name='结束时间', null=True,
    blank=True)
    # auto_now_add ⾃动将当前时间添加到数据库
    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

""" 项⽬表 """
class Project(models.Model):
    COLOR_CHOICES = (
    (1, "#56b8eb"), # 蓝⾊
    (2, "#f28033"), # 橘⻩
    (3, "#ebc656"), # 浅⻩
    (4, "#a2d148"), # 浅绿
    (5, "#20BFA4"), # 墨绿
    (6, "#7461c2"), # 紫⾊
    (7, "#20bfa3"), # 深绿
    )
    name = models.CharField(verbose_name='项⽬名', max_length=32)
    color = models.SmallIntegerField(verbose_name='颜⾊', choices=COLOR_CHOICES, default=1)
    desc = models.CharField(verbose_name='项⽬描述', max_length=255, null=True, blank=True)
    use_space = models.BigIntegerField(verbose_name='项⽬已使⽤空间', default=0, help_text='字节')
    star = models.BooleanField(verbose_name='星标', default=False)
    join_count = models.SmallIntegerField(verbose_name='参与⼈数', default=1)
    creator = models.ForeignKey(verbose_name='创建者', to='UserInfo', on_delete=models.CASCADE)
    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

""" 项⽬参与者 """
class ProjectUser(models.Model):
    project = models.ForeignKey(verbose_name='项⽬', to='Project', on_delete=models.CASCADE)
    user = models.ForeignKey(verbose_name='参与者', to='UserInfo', on_delete=models.CASCADE)
    star = models.BooleanField(verbose_name='星标', default=False)
    create_datetime = models.DateTimeField(verbose_name='加⼊时间', auto_now_add=True)