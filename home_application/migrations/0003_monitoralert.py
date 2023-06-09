# Generated by Django 3.2.4 on 2023-05-21 08:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home_application', '0002_jobexecutehistory'),
    ]

    operations = [
        migrations.CreateModel(
            name='MonitorAlert',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bk_biz_id', models.IntegerField(verbose_name='业务ID')),
                ('alert_id', models.CharField(max_length=64, unique=True, verbose_name='告警ID')),
                ('name', models.CharField(max_length=255, verbose_name='告警名称')),
                ('severity', models.IntegerField(choices=[(1, '致命'), (2, '预警'), (3, '提醒')], verbose_name='告警级别')),
                ('category', models.CharField(max_length=255, verbose_name='分类')),
                ('category_display', models.CharField(max_length=255, verbose_name='分类名称')),
                ('status', models.CharField(choices=[('ABNORMAL', '未恢复'), ('RECOVERED', '已恢复'), ('CLOSED', '已关闭')], max_length=16, verbose_name='当前状态')),
                ('is_shielded', models.BooleanField(default=False, verbose_name='是否被屏蔽中')),
                ('assignee', models.JSONField(default=list, verbose_name='负责人')),
                ('is_ack', models.BooleanField(default=False, verbose_name='是否确认')),
                ('is_handled', models.BooleanField(default=False, verbose_name='是否处理')),
                ('strategy_id', models.IntegerField(verbose_name='策略ID')),
                ('strategy_name', models.CharField(max_length=255, verbose_name='策略名称')),
                ('ack_operator', models.CharField(blank=True, default='', max_length=64, verbose_name='确认人')),
                ('bk_cloud_id', models.IntegerField(null=True, verbose_name='云区域ID')),
                ('ip', models.CharField(blank=True, max_length=128, null=True, verbose_name='目标IP')),
                ('begin_time', models.DateTimeField(verbose_name='告警开始时间')),
                ('create_time', models.DateTimeField(verbose_name='告警生成时间')),
                ('latest_time', models.DateTimeField(verbose_name='最近异常时间')),
                ('end_time', models.DateTimeField(null=True, verbose_name='结束时间')),
                ('update_time', models.DateTimeField(verbose_name='更新时间')),
            ],
        ),
    ]
