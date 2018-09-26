#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio

from datetime import datetime
from functools import reduce
from inspect import isawaitable
from signal import SIGINT, SIGTERM
from types import AsyncGeneratorType

from aspider.middleware import Middleware
from aspider.request import Request
from aspider.utils import get_logger

try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

except Exception:
    pass


class Spider:
    name = 'aspider'
    request_config = None

    failed_counts, success_counts = 0, 0
    start_urls, worker_tasks = [], []

    def __init__(self, middleware, loop=None):
        if not self.start_urls or not isinstance(self.start_urls, list):
            raise ValueError("Spider must have a param start_urls")

        self.logger = get_logger(name=self.name)
        self.loop = loop or asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        # customize middleware
        if isinstance(middleware, list):
            self.middleware = reduce(lambda x, y: x + y, middleware)
        else:
            self.middleware = middleware or Middleware()

        # async queue
        self.request_queue = asyncio.Queue()

        # semaphore
        self.sem = asyncio.Semaphore(getattr(self, 'concurrency', 3))

    async def parse(self, res):
        raise NotImplementedError

    @classmethod
    def start(cls, after_start=None,
              before_stop=None,
              middleware=None,
              loop=None):
        """
        Start a spider
        :param after_start:
        :param before_stop:
        :param middleware:
        :param loop:
        :return:
        """
        spider_ins = cls(middleware=middleware, loop=loop)
        spider_ins.logger.info('Spider started!')
        start_time = datetime.now()

        if after_start:
            result = after_start(spider_ins.loop)
            if isawaitable(result):
                spider_ins.loop.run_until_complete(result)

        for _signal in (SIGTERM, SIGINT):
            try:
                spider_ins.loop.add_signal_handler(_signal,
                                                   lambda : asyncio.ensure_future(spider_ins.stop(_signal)))
            except NotImplementedError:
                spider_ins.logger.warning(f'{spider_ins.name} tried to use loop.add_signal_handler '
                                          'but it is not implemented on this platform.')


        asyncio.ensure_future(spider_ins.start_master())

        try:
            spider_ins.loop.run_forever()
        finally:
            if before_stop:
                result = before_stop(spider_ins.loop)
                if isawaitable(result):
                    spider_ins.loop.run_until_complete(result)

            end_time = datetime.now()
            spider_ins.logger.info(f'Total requests: {spider_ins.failed_counts + spider_ins.success_counts}')

            if spider_ins.failed_counts:
                spider_ins.logger.info(f'Failed request: {spider_ins.failed_counts}')

            spider_ins.logger.info(f'Time usage: {end_time - start_time}')
            spider_ins.logger.info('Spider finished!')
            spider_ins.loop.run_until_complete(spider_ins.loop.shutdown_asyncgens())
            spider_ins.loop.close()

    async def handler_request(self, request):
        await self._run_request_middleware(request)
        callback_res, response = await request.fetch_callback(self.sem)
        await self._run_response_middleware(request, response)
        return callback_res, response

    async def start_master(self):
        for url in self.start_urls:
            request_ins = Request(
                url=url,
                callback=self.parse,
                headers=getattr(self, 'headers', {}),
                load_js=getattr(self, 'load_js', False),
                metadata=getattr(self, 'metadata', None),
                request_config=getattr(self, 'request_config'),
                request_session=getattr(self, 'request_session', None),
                res_type=getattr(self, 'res_type', 'text'),
                **getattr(self, 'kwarg', {})
            )
            self.request_queue.put_nowait(self.handler_request(request_ins))

        workers = [asyncio.ensure_future(self.start_worker()) for i in range(2)]
        await self.request_queue.join()
        await self.stop(SIGINT)

    async def start_worker(self):
        while True:
            request_item = await self.request_queue.get()
            self.worker_tasks.append(request_item)

            if self.request_queue.empty():
                results = await asyncio.gather(*self.worker_tasks, return_exceptions=True)
                for task_result in results:
                    if not isinstance(task_result, RuntimeWarning):
                        callback_res, res = task_result
                        if isinstance(callback_res, AsyncGeneratorType):
                            async for request_ins in callback_res:
                                self.request_queue.put_nowait(self.handler_request(request_ins))

                        if res.html is None:
                            self.failed_counts += 1
                        else:
                            self.success_counts += 1
                self.worker_tasks = []
            self.request_queue.task_done()

    async def stop(self, _signal):
        self.logger.info(f'Stropping spider: {self.name}')
        tasks = [task for task in asyncio.Task.all_tasks() if task is not
                 asyncio.tasks.Task.current_task()]
        list(map(lambda task: task.cancel(), tasks))
        results = await asyncio.gather(*tasks, return_exceptions=True)
        self.loop.stop()

    async def _run_request_middleware(self, request):
        if self.middleware.request_middleware:
            for middleware in self.middleware.request_middleware:
                middleware_func = middleware(request)
                if isawaitable(middleware_func):
                    try:
                        reult = await middleware_func
                    except Exception as e:
                        self.logger.exception(e)
                else:
                    self.logger.error('Middleware must be a coroutine function')
                    result = None

    async def _run_response_middleware(self, request, response):
        if self.middleware.response_middleware:
            for middleware in self.middleware.response_middleware:
                middleware_func = middleware(request, response)
                if isawaitable(middleware_func):
                    try:
                        result = await middleware_func
                    except Exception as e:
                        self.logger.exception(e)

                else:
                    self.logger.error('Middleware must be a coroutine function')
                    result = None














