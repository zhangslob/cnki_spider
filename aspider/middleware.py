#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import deque
from functools import wraps


class Middleware:

    def __init__(self):
        self.request_middleware = deque()
        self.response_middleware = deque()

    def listener(self, uri, target, **kwargs):
        def register_middleware(middleware):
            if target == 'request':
                self.request_middleware.append(middleware)
            if target == 'response':
                self.response_middleware.append(middleware)
            return middleware

        return register_middleware

    def request(self, *args, **kwargs):
        middleware = args[0]

        @wraps(middleware)
        def register_middleware(*args, **kwargs):
            self.request_middleware.append(middleware)
            return middleware

        return register_middleware()

    def response(self, *args, **kwargs):
        middleware = args[0]

        @wraps(middleware)
        def register_middleware(*args, **kwargs):
            self.response_middleware.append(middleware)
            return middleware

        return register_middleware()

    def __add__(self, other):
        new_middleware = Middleware()

        new_middleware.response_middleware.extend(self.request_middleware)
        new_middleware.response_middleware.extend(other.request_middleware)

        new_middleware.response_middleware.extend(self.response_middleware)
        new_middleware.response_middleware.extend(other.response_middleware)
        return new_middleware
