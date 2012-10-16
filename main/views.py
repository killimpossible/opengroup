#coding=utf-8

'''
@author: 潘飞(cnweike@gmail.com)
'''

from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required

from models import *
import settings

import os
import hashlib
import random

GROUPS_FOR_ONE = 3

def judge_role(request, group_id):
    '''判断用户角色的工具函数'''
    me = request.user
    me.is_member = False;me.is_manager=False;me.is_owner=False
    
    try:
        the_group = Group.objects.get(id=group_id)
    except:
        the_group = None
        
    if me.is_authenticated():
        try:
            the_rel = me.member_gms.select_related().get(group=the_group)
            me.rel = the_rel
            me.is_member = True
            if the_rel.member_role == MEMBER_ROLE_CHOICES[1][1]:
                me.is_manager = True
            elif the_rel.member_role == MEMBER_ROLE_CHOICES[2][1]:
                me.is_owner = True
            return the_group, me
        except:
            return the_group, me
    else:
        return the_group, me


def sign_up(request, template):
    '''注册用户'''
    if request.user.is_authenticated():
        return HttpResponseRedirect("/")
    if request.method == 'GET':
        return render_to_response(template, {}, context_instance=RequestContext(request))
    elif request.method == 'POST':
        data = request.POST
        username = data.get('username', '')
        email = data.get('email', '')
        password = data.get('password', '')
        auth_code = data.get('auth_code', '')
        
        err_message = ''
        user_of_the_username = None
        try:
            user_of_the_username = User.objects.get(username=username)
        except:
            pass
        
        if user_of_the_username:
            err_message = "The username is already taken ."
        elif auth_code.lower() != request.session['auth_code'].lower():
            err_message = "Auth-code is not correct, please retry ."
        elif username.strip() == '':
            err_message = "User should not be null ."
        elif len(password.strip()) < 6:
            err_message = "Password is too short (6 or more is required)."
        else:
            user_of_the_email = User.objects.filter(email=email)
            if user_of_the_email:
                err_message = "The email is already taken ."
                return render_to_response('services/reg.html', {'err_message':err_message})
            new_user = User.objects.create_user(username, email, password)
            new_user.is_active = False
            new_user.save()
            s_str = settings.SECRET_KEY + ":" + str(new_user.id)
            s_str = hashlib.md5(s_str).hexdigest()
            email_string = render_to_string('services/activate_email.html', {'password':password, 'new_user':new_user, 's_str':s_str})
            subject, from_email, to = 'OpenGroup activation Mail', 'yookoyoo@gmail.com', email
            msg = EmailMultiAlternatives(subject, "This is OpenGroup activation Mail", from_email, [to])
            msg.attach_alternative(email_string, "text/html")
            msg.send()
            return render_to_response('services/status.html', {'email':email, 'reg_send_mail':True}, context_instance=RequestContext(request))
        return render_to_response('services/reg.html', {'err_message':err_message})  

def activate_account(request):
    '''account activate'''
    data = request.GET
    user_id = data.get('id', '')
    s_str = data.get('s_str', '')
    the_user = User.objects.filter(id=user_id)[0]
    if the_user.is_active:
        return render_to_response('services/status.html', {'account_activate':True, 'activated':True}, context_instance=RequestContext(request))
    r_str = settings.SECRET_KEY + ":" + str(user_id)
    r_str = hashlib.md5(r_str).hexdigest()
    if s_str == r_str:
        the_user.is_active = True
        the_user.save()
        return render_to_response('services/status.html', {'account_activate':True, 'success':True}, context_instance=RequestContext(request))
    else:
        return render_to_response('services/status.html', {'account_activate':True, 'success':False}, context_instance=RequestContext(request))

def log_out(request):
    '''登出用户'''
    logout(request)
    return HttpResponseRedirect("/")

def log_in(request, template):
    '''登录用户'''
    if request.user.is_authenticated():
        return HttpResponseRedirect("/")
    if request.method == 'GET':
        next = request.GET.get('next', '')
        return render_to_response(template, {'next':next}, context_instance=RequestContext(request))
    elif request.method == 'POST':
        data = request.POST
        email = data.get('email', '')
        password = data.get('password', '')
        user = authenticate(email=email, password=password)
        if not user:
            return render_to_response(template, {'err_message':'Email does not exist or wrong password.'}, context_instance=RequestContext(request))
        else:
            if user.is_active:
                login(request, user)
                next = request.POST.get('next', '')
                if next:
                    return HttpResponseRedirect(next)
                else:
                    return HttpResponseRedirect("/user_center/")
            else:
                return render_to_response(template, {'err_message':'Account not activated .'}, context_instance=RequestContext(request))

@login_required
def user_center(request, template):
    '''用户中心'''
    me = request.user
    groups_joined = me.member_gms.select_related().exclude(group__creator=me).order_by("-create_time")
    groups_my = me.member_gms.select_related().filter(group__creator=me).order_by("-create_time")
    
    
    return render_to_response(template, {'groups_joined':groups_joined, 'groups_my':groups_my}, context_instance=RequestContext(request))
    
def start(request, template):
    '''到开始页面'''
    latest_topics = Topic.objects.select_related().all().order_by('-create_time')[:16]
    return render_to_response(template, {'latest_topics':latest_topics}, context_instance=RequestContext(request))

def topic_detail(request, template, group_id, topic_id):
    '''具体话题内容显示'''
    topic_id = int(topic_id)
    group_id = int(group_id)
    the_group, me = judge_role(request, group_id)
    
    try:
        the_topic = Topic.objects.get(id=topic_id)
    except:
        return render_to_response('services/err.html', {'err_msg':'Invalid topic'}, context_instance=RequestContext(request))
    
    replies = the_topic.topic_replies.all().order_by('-create_time')
    return render_to_response(template, {'topic':the_topic, 'replies':replies}, context_instance=RequestContext(request))

@login_required
def add_reply(request, group_id, topic_id):
    '''添加回应'''
    topic_id = int(topic_id)
    group_id = int(group_id)
    the_group, me = judge_role(request, group_id)
    
    if request.method == 'GET':
        return HttpResponseRedirect('/groups/%s/topics/%s/'%(group_id, topic_id)) 
    
    if not me.is_member:
        return render_to_response('services/err.html', {'err_msg':'You are not a member of the group, so you cannot reply.'}, context_instance=RequestContext(request))
    
    try:
        the_topic = Topic.objects.select_related().get(id=topic_id)
    except:
        the_topic = None
    
    if the_topic.group != the_group:
        the_topic = None
    
    if not the_topic:
        return render_to_response('services/err.html', {'err_msg':'Invalid topic.'}, context_instance=RequestContext(request))
    
    content = request.POST.get('reply_content', '')
    
    if content.strip():
        reply = Reply()
        reply.creator = me
        reply.content = content
        reply.topic = the_topic
        tra, created = Topic_reply_amount.objects.get_or_create(topic=the_topic)
        if created:
            tra.amount = 1
        else:
            tra.amount += 1
        try:
            reply.save()
            tra.save()
            return HttpResponseRedirect('/groups/%s/topics/%s/'%(group_id, topic_id))
        except:
            return render_to_response('services/err.html', {'err_msg':'error happens.'}, context_instance=RequestContext(request))
        
def group_detail(request, template, group_id):
    '''具体小组信息'''
    group_id = int(group_id)
    the_group, me = judge_role(request, group_id)
    topics = the_group.group_topics.all().order_by('-last_reply_add', '-create_time')
    return render_to_response(template, {'group':the_group, 'topics':topics}, context_instance=RequestContext(request))           

@login_required
def join_group(request, group_id):
    '''加入小组'''
    group_id = int(group_id)
    the_group, me = judge_role(request, group_id)
    if not the_group:
        return render_to_response('services/err.html', {'err_msg':'no such group.'}, context_instance=RequestContext(request))
    else:
        if not me.is_member:
            gm = Group_memeber()
            gm.group = the_group
            gm.member = me
            gm.save()
    return HttpResponseRedirect("/groups/%s/"%group_id)

@login_required
def with_draw(request, group_id):
    '''退出小组'''
    group_id = int(group_id)
    the_group, me = judge_role(request, group_id)
    if not the_group:
        return render_to_response('services/err.html', {'err_msg':'no such group.'}, context_instance=RequestContext(request))
    else:
        if me.is_member:
            rel = me.rel
            rel.delete()
            del me.rel
    return HttpResponseRedirect("/groups/%s/"%group_id)

@login_required
def create_group(request, template):
    '''创建小组'''
    me = request.user
    if request.method == 'GET':
        return render_to_response(template, {}, context_instance=RequestContext(request))
    elif request.method == 'POST':
        group_name = request.POST.get('group_name', '')
        group_description = request.POST.get('group_description', '')
        is_open = request.POST.get('is_open', '')
        member_join = request.POST.get('mem_join', '')
        
        gs = Group.objects.filter(creator=me)
        if gs.count()>=GROUPS_FOR_ONE:
            return render_to_response('services/err.html', {'err_msg':'Everyone allowed to create %s group.'%GROUPS_FOR_ONE}, context_instance=RequestContext(request)) 

        
        if not(group_name.strip() and group_description.strip() and is_open and member_join):
            return render_to_response('services/err.html', {'err_msg':'group information not complete.'}, context_instance=RequestContext(request)) 
        else:
            group = Group()
            group.name = group_name
            group.description = group_description
            group.creator = me
            group.is_open = is_open
            group.member_join = member_join
            group.save()
        
            gm = Group_memeber()
            gm.group = group
            gm.member = me
            gm.member_role = 2
            gm.save()
            
            gta = Group_topic_amount()
            gta.group = group
            gta.save()
            
            return HttpResponseRedirect("/user_center/")
            
@login_required
def create_topic(request, template, group_id):
    '''创建话题'''
    group_id = int(group_id)
    the_group, me = judge_role(request, group_id)
    
    if request.method == 'GET':
        return render_to_response(template, {'group':the_group}, context_instance=RequestContext(request))
    
    if not the_group:
        return render_to_response('services/err.html', {'err_msg':'no such group.'}, context_instance=RequestContext(request))
    else:
        if me.is_member:
            topic_name = request.POST.get('topic_name', '')
            topic_content = request.POST.get('topic_content', '')
            if topic_name.strip() and topic_content.strip():
                topic = Topic()
                topic.name = topic_name
                topic.content = topic_content
                topic.creator = me
                topic.group = the_group
                gta, created = Group_topic_amount.objects.get_or_create(group=the_group)
                if created:
                    gta.amount = 1
                else:
                    gta.amount += 1
                gta.save()
                
                topic.save()
                tra = Topic_reply_amount()
                tra.topic = topic
                tra.save()
                return HttpResponseRedirect("/groups/%s/"%group_id)
            else:
                return render_to_response('services/err.html', {'err_msg':'topic name or content is not allowed leave blank.'}, context_instance=RequestContext(request))
        else:
            return render_to_response('services/err.html', {'err_msg':'You are not a member'}, context_instance=RequestContext(request))

def search(request):
    '''按照小组或者话题，搜索'''
    if request.method == 'GET':
        search_type = request.GET.get('search_type', '')
        q = request.GET.get('q', '')
        
        if not search_type.strip():
            return render_to_response('services/err.html', {'err_msg':'invalid request'}, context_instance=RequestContext(request))
        
        from django.utils.encoding import iri_to_uri
        from django.utils.http import urlquote
        
        if search_type == '0':
            return HttpResponseRedirect(iri_to_uri(u'/group_list/?q=%s'%(q)))
        else:
            return HttpResponseRedirect(iri_to_uri(u'/topic_list/?q=%s'%(q)))
    elif request.method == 'POST':
        return HttpResponseRedirect("/")

def group_list(request, template):
    '''小组列表'''
    q = request.GET.get('q', '').strip()
    if q:
        groups = Group.objects.filter(name__icontains=q).order_by('-create_time')
    else:
        groups = Group.objects.all().order_by('-create_time')
    
    return render_to_response(template, {'groups':groups}, context_instance=RequestContext(request))

def topic_list(request, template):
    '''话题列表'''
    q = request.GET.get('q', '').strip()
    if q:
        topics = Topic.objects.filter(name__icontains=q).order_by('-create_time')
    else:
        topics = Topic.objects.all().order_by('-create_time')
    
    return render_to_response(template, {'topics':topics}, context_instance=RequestContext(request))

def latest_topics(request, template):
    '''最新话题'''
    topics = Topic.objects.all().order_by('-create_time')
    return render_to_response(template, {'topics':topics}, context_instance=RequestContext(request))

def hottest_topics(request, template):
    '''最热话题'''
    rels = Topic_reply_amount.objects.all().order_by('-amount')
    topics = [rel.topic for rel in rels]
    return render_to_response(template, {'topics':topics}, context_instance=RequestContext(request))

def latest_groups(request, template):
    '''最新小组'''
    groups = Group.objects.all().order_by('-create_time')
    return render_to_response(template, {'groups':groups}, context_instance=RequestContext(request))

def hottest_groups(request, template):
    '''最热小组'''
    rels = Group_topic_amount.objects.all().order_by('-amount')
    groups = [rel.group for rel in rels]
    return render_to_response(template, {'groups':groups}, context_instance=RequestContext(request))
    
def get_check_code_image(request):
    '''生成验证码'''
    import Image, ImageDraw, ImageFont, cStringIO ,string
    bgcolor = (0, 100, 0)
    image = Image.new('RGB',(150,16),bgcolor)
    font_file = os.path.join(os.path.dirname(__file__), '../site_media/fonts/ARIAL.TTF').replace('\\', '/')
    font = ImageFont.truetype(font_file,16)
    fontcolor = (0, 0, 0)
    draw = ImageDraw.Draw(image)
    
    rand_str = ''
    for i in range(4):
        rand_str += random.choice(string.letters + string.digits)
        
    draw.text((35,0),rand_str,font=font,fill=fontcolor)
    del draw
    request.session['auth_code'] = rand_str
    buf = cStringIO.StringIO()
    image.save(buf, 'jpeg')
    return HttpResponse(buf.getvalue(),'image/jpeg') 