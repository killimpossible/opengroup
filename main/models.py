#coding=utf-8

'''
@author: 潘飞(cnweike@gmail.com)
'''

from django.db import models
from django.contrib.auth.models import User

import datetime

GROUP_TYPE_CHOICES = ((0, 'Open'), (1, 'Private'))
MEMBER_ROLE_CHOICES = ((0, 'Member'), (1, 'Manager'), (2, 'Owner'))
MEMBER_JOIN_CHOICES = ((0, 'Everyone can join'), (1, 'Need check'))

class Group(models.Model):
    '''小组模式'''
    name = models.CharField(max_length=1024, verbose_name='小组名称')
    description = models.TextField(blank=True, verbose_name='小组描述')
    image = models.ImageField(upload_to='group_images/%Y/%m/%d', blank=True, null=True, verbose_name='小组图片')
    creator = models.ForeignKey(User, related_name='created_groups', verbose_name='小组创建人')
    type = models.SmallIntegerField(default=0, choices=GROUP_TYPE_CHOICES, verbose_name='小组类型')
    member_join = models.SmallIntegerField(default=0, choices=MEMBER_JOIN_CHOICES, verbose_name='用户加入方式')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='小组创建时间')
    modify_time = models.DateTimeField(auto_now=True, verbose_name='上次修改时间')
    is_closed = models.BooleanField(default=False, verbose_name='是否被关闭')
    last_topic_add = models.DateTimeField(default=datetime.datetime.now(), verbose_name='最后一个话题创建的时间')
    
    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = '小组'
        verbose_name_plural = '小组'
        

class Group_topic_amount(models.Model):
    '''小组话题总量'''
    group = models.ForeignKey(Group, unique=True, related_name='group_topic_amounts', verbose_name='小组')
    amount = models.IntegerField(default=0, verbose_name='小组话题总量')
    
    def __unicode__(self):
        return unicode(self.amount)
    
    class Meta:
        verbose_name = '小组及其话题总量'
        verbose_name_plural = '小组及其话题总量'
    
class Topic(models.Model):
    '''话题模式'''
    name = models.CharField(max_length=1024, verbose_name='话题名称')
    content = models.TextField(verbose_name='话题内容')
    group = models.ForeignKey(Group, related_name='group_topics', verbose_name='小组')
    creator = models.ForeignKey(User, related_name='created_topics', verbose_name='话题创建者')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    modify_time = models.DateTimeField(auto_now=True, verbose_name='修改时间')
    is_closed = models.BooleanField(default=False, verbose_name='话题是否被关闭')
    last_reply_add = models.DateTimeField(default=datetime.datetime.now(), verbose_name='最后一个回应的创建时间')
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        verbose_name = '话题'
        verbose_name_plural = '话题'
    
    def save(self, force_insert=False, force_update=False):
        self.group.last_topic_add = datetime.datetime.now()
        self.group.save()
        super(Topic, self).save(force_insert, force_update)

class Topic_reply_amount(models.Model):
    '''话题回应总量'''
    topic = models.ForeignKey(Topic, unique=True, related_name='topic_reply_amounts', verbose_name='话题')
    amount = models.IntegerField(default=0, verbose_name='话题回应总量')
    
    def __unicode__(self):
        return unicode(self.amount)
    
    class Meta:
        verbose_name = '话题及其回应总量'
        verbose_name_plural = '话题及其回应总量'
    
class Reply(models.Model):
    '''回应表'''
    content = models.TextField(verbose_name='回应内容')
    creator = models.ForeignKey(User, related_name='created_replies', verbose_name='回应创建者')
    topic = models.ForeignKey(Topic, related_name='topic_replies', verbose_name='回应的话题')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='回应创建时间')
    
    def __unicode__(self):
        return self.topic.name
    
    class Meta:
        verbose_name = '回应'
        verbose_name_plural = '回应'

    def save(self, force_insert=False, force_update=False):
        self.topic.last_reply_add = datetime.datetime.now()
        self.topic.save()
        super(Reply, self).save(force_insert, force_update)

class Group_memeber(models.Model):
    '''小组-成员关系模式'''
    group = models.ForeignKey(Group, related_name='group_gms', verbose_name='小组')
    member = models.ForeignKey(User, related_name='member_gms', verbose_name='成员')
    member_role = models.SmallIntegerField(default=0, choices=MEMBER_ROLE_CHOICES, verbose_name='成员角色')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    def __unicode__(self):
        return self.group.name
    
    class Meta:
        verbose_name = '小组成员关系'
        verbose_name_plural = '小组成员关系'
        unique_together = (("group", "member"),)
        
