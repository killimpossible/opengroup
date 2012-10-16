#coding=utf-8

'''
@author: 潘飞(cnweike@gmail.com)
'''

from django.conf.urls.defaults import *

import settings
from views import *

urlpatterns = patterns('',
    (r'^site_media/(?P<path>.*)$','django.views.static.serve', {'document_root':settings.STATIC_PATH}),
    (r'^upload_files/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    (r'^$', start, {'template':'start.html'}),
    (r'^groups/(?P<group_id>\d*)/$', group_detail, {'template':'services/group_detail.html'}),
    (r'^groups/(?P<group_id>\d*)/topics/(?P<topic_id>\d*)/$', topic_detail, {'template':'services/topic_detail.html'}),
    (r'^groups/(?P<group_id>\d*)/topics/(?P<topic_id>\d*)/add_reply/$', add_reply),
    (r'^groups/(?P<group_id>\d*)/join_group/$', join_group),
    (r'^groups/(?P<group_id>\d*)/with_draw/$', with_draw),
    (r'^groups/(?P<group_id>\d*)/create_topic/$', create_topic, {'template':'services/create_topic.html'}),
    (r'^groups/create_group/$', create_group, {'template':'services/create_group.html'}),
    (r'^group_list/$', group_list, {'template':'services/group_list.html'}),
    (r'^latest_groups/$', latest_groups, {'template':'services/group_list.html'}),
    (r'^hottest_groups/$', hottest_groups, {'template':'services/group_list.html'}),
    (r'^topic_list/$', topic_list, {'template':'services/topic_list.html'}),
    (r'^latest_topics/$', latest_topics, {'template':'services/topic_list.html'}),
    (r'^hottest_topics/$', hottest_topics, {'template':'services/topic_list.html'}),
    (r'^search/$', search),
    (r'^log_out/$', log_out),
    (r'^log_in/$', log_in, {'template':'services/login.html'}),
    (r'^user_center/$', user_center, {'template':'services/user_center.html'}),
    (r'^sign_up/$', sign_up, {'template':'services/reg.html'}),
    (r'^activate_account/$',activate_account),
    (r'^get_check_code_image/$', get_check_code_image),
)