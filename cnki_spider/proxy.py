#!/usr/bin/env python3
# coding:utf-8
import csv
import random
import os
class ProxyPool(object):

    _instance = None

    # 建立可分配IP队列
    _live_ip_queues = []
    # 建立回收队列
    _dell_ip_queues = []
    # 建立IP计数队列
    _life_ip_queues = {}
    # 建立IP用户名密码
    _user_ip_queues = {}

    def __new__(cls, *args, **kw):
        if not cls._instance:
            cls._instance = super(ProxyPool, cls).__new__(cls, *args, **kw)
        return cls._instance


    def __init__(self):
        # 代理格式 "http://112.25.41.136:80"
        # 账号密码的代理格式 "http://user:password@112.25.41.136:80"
        # 读取数据

        with open(os.path.abspath('proxylist.csv'), 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                self._user_ip_queues[row['user']] = row['host']
                #self._live_ip_queues.append("http://{0}:{1}@{2}".format(row['user'], row['password'], row['host']))
                self._live_ip_queues.append("https://{0}@{1}".format(row['user'], row['host']))


    def get(self):
        proxy = False
        try:
            while not proxy:

                if len(self._live_ip_queues) < 10:
                    self._live_ip_queues.extend(self._dell_ip_queues[:12])
                    self._dell_ip_queues = self._dell_ip_queues[12:]

                proxy = self._live_ip_queues[random.randint(0, len(self._live_ip_queues))]

                # if proxy in self._life_ip_queues.keys():
                if proxy in self._life_ip_queues:
                    if self._life_ip_queues[proxy] > 6:
                        self._life_ip_queues.pop(proxy)
                        self._live_ip_queues.remove(proxy)
                        self._dell_ip_queues.append(proxy)
                        proxy = False
                    else:
                        self._life_ip_queues[proxy] += 1

                else:
                    self._life_ip_queues[proxy] = 1
        except Exception:
            pass
        return proxy

        #return self._live_ip_queues[random.randint(0, len(self._live_ip_queues))]
        pass

    def change_ip(self, proxy):

        if proxy in self._user_ip_queues:
            proxy = "http://{0}@{1}".format(self._user_ip_queues[proxy], proxy)
            try:
                self._live_ip_queues.remove(proxy)
                self._dell_ip_queues.append(proxy)
            except Exception:
                pass

    def revival_ip(self):
        pass

    def in_live_pool(self, ip):
        return ip in self._live_ip_queues

class ProxyValve(object):

    @classmethod
    def get_ip(cls):
        proxy_pool = ProxyPool()
        return proxy_pool.get()

    @classmethod
    def change_ip(cls, proxy):
        ProxyPool().change_ip(proxy)

    @classmethod
    def in_pool(cls, ip):
        proxy_pool = ProxyPool()
        return proxy_pool.in_live_pool(ip)

p = ProxyValve()
print(p.get_ip())
