#!/usr/bin/env python
# -*- coding: utf-8 -*-

import signal
import sys
import requests
import threading
import queue
import time
from bs4 import BeautifulSoup

mutex = threading.Lock()
is_exist = False


class Tumblr(threading.Thread):
    def __init__(self, queue):
        super(Tumblr, self).__init__(queue)
        self.user_queue = queue
        self.total_user = []
        self.total_url = []
        self.f_user = open('user.txt', 'a+')
        self.f_source = open('source', 'a+')

    def download(self, url):
        res = requests.get(url)

        source_list = []
        soup = BeautifulSoup(res.text)
        iframes = soup.find_all('iframe')
        tmp_source = []

        for i in iframes:
            source = i.get('src', '').strip()
            if soup and soup.find('https://www.tumblr.com/video') != -1 and source not in self.total_url:
                source_list.append(source)
                tmp_source.append(source)
                print('get more url {}'.format(source))

        tmp_user = []
        new_users = soup.find_all(class_='reblog-link')
        for user in new_users:
            username = user.text.strip()
            if username and username not in self.total_user:
                self.user_queue.put(username)
                self.total_user.append(username)
                tmp_user.append(username)
                print('get more user {}'.format(username))

        mutex.acquire()
        if tmp_user:
            self.f_user.write('\n'.join(tmp_user) + '\n')
        if tmp_source:
            self.f_source.write('\n'.join(tmp_source) + '\n')

        mutex.release()

    def run(self):
        global is_exist
        while not is_exist:
            user = self.user_queue.get()
            url = 'http://{}.tumblr.com/'.format(user)
            self.download(url)
            time.sleep(2)
        self.f_user.close()
        self.f_source.close()


def handler(signum, frame):
    global is_exist
    is_exist = True
    print('receive a signal {}, is_exist is {}'.format(signum, frame))
    sys.exit(0)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('usage: python tumblr.py username')
        sys.exit(0)
    username = sys.argv[1]

    NUM_WORKERS = 10
    q = queue.Queue()
    q.put(username)

    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)

    threads = []
    for i in range(NUM_WORKERS):
        tumblr = Tumblr(q)
        tumblr.setDaemon(True)
        tumblr.start()
        threads.append(tumblr)

    while True:
        for i in threads:
            if not i.isAlive():
                break
        time.sleep(2)
