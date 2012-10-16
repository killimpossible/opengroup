#coding=utf8

'''
@author: 潘飞(cnweike@gmail.com)
'''

class MainMiddleware(object):
    def process_request(self, request):
        '''一开始想用来判定用户身份，但是考虑后就不用了了， 把这部分功能封装到了一个函数中实现'''
        pass
                