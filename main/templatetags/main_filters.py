#coding=utf-8

'''
@author: 潘飞(cnweike@gmail.com)
'''

from django import template
register = template.Library()

@register.filter
def limit(value,limit):
    '''需要一个长度参数'''
    limit = int(limit)
    addspots = False
    if len(value) > limit:
        addspots = True
    value = value[:limit]
    if addspots:
        value += '...'
    return value