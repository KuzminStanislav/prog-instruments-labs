from collections import Counter
import time
from typing import Optional

import aiohttp
import asyncio

from test_config import TestConfig, RequestResult
from statistics import TestStatistics, format_status_code


class LoadTester:
    """
    Class for load test
    """
    def __init__(self, config: TestConfig):
        """
        Class initialization
        :param config: Test config
        """
        self.config = config
        self.results = list[RequestResult] = []
        self.start_time = Optional[float] = None
        self.status_codes = Counter()

        self.timeout_errors = 0
        self.connection_errors = 0
        self.http_errors_5xx = 0


    async def make_request(
            self, 
            session: aiohttp.ClientSession,
            request_id: int
        ) -> None:
        """
        Do 1 http request and save result
        :param session: Session for doing request
        :param request_id: Id of request 
        """
        request_start = time.time()

        try:
            async with session.get(
                self.config.url,
                timeout = aiohttp.ClientTimeout(total = self.config.wait_timeout)
            ) as response:
                response_time = (time.time() - request_start) * 1000

                result = RequestResult(
                    request_id = request_id,
                    status_code = response.status,
                    response_time = response_time,
                    error = None
                )

                self.results.append(result)
                self.status_codes[response.status] += 1

                if response.status >= 500:
                    self.http_errors_5xx += 1

        except asyncio.TimeoutError:
            result = RequestResult(
                request_id = request_id,
                status_code = 'TIMEOUT',
                response_time = self.config.wait_timeout * 1000,
                error = 'Timeout'
            )

            self.results.append(result)
            self.timeout_errors += 1
            self.status_codes['TIMEOUT'] += 1

        except aiohttp.ClientConnectionError:
            result = RequestResult(
                request_id=request_id,
                status_code='CONNECTION_ERROR',
                response_time=(time.time() - request_start) * 1000,
                error='connection'
            )

            self.results.append(result)
            self.connection_errors += 1
            self.status_codes['CONNECTION_ERROR'] += 1
            
        except Exception as e:
            result = RequestResult(
                request_id=request_id,
                status_code='OTHER_ERROR',
                response_time=(time.time() - request_start) * 1000,
                error=str(e)
            )

            self.results.append(result)
            self.status_codes['OTHER_ERROR'] += 1


    async def worker(
            self,
            session: aiohttp.ClientSession,
            queue: asyncio.Queue
        ) -> None:
        """
        Work process
        :param session: Session for doing request
        :param queue: Queue with id's
        """
        while True:
            request_id = await queue.get()
            if request_id is None:
                queue.task_done()
                break

            await self.make_request(session, request_id)
            queue.task_done()

    
    async def run_load_test(self) -> TestStatistics:
        """
        Run load test
        :return: Statistics of finished test
        """
        self._print_test_info()
        self.start_time = time.time()

        connector = aiohttp.TCPConnector(limit = 0, limit_per_host = 0)
        async with aiohttp.ClientSession(connector = connector) as session:
            queue = asyncio.Queue()
            workers = await self._start_workers(session, queue)
            await self._distribute_requests(queue)
            await queue.join()
            await self._stop_workers(queue, workers)
        
        await asyncio.sleep(self.config.wait_timeout)
        return TestStatistics(self.results)
    

    async def _start_workers(
            self, 
            session: aiohttp.ClientSession,
            queue: asyncio.Queue
        ) -> list[asyncio.Task]:
        """
        Start working processes
        :param session: Session for workers
        :param queue: Queue of tasks
        :return: list with tasks
        """
        num_workers = min(self.config.rps * 2, 1000)

        workers = [
            asyncio.create_task(self.worker(session, queue))
            for _ in range(num_workers)
        ]

        return workers
    

    async def _distribute_requests(
            self,
            queue: asyncio.Queue
    ) -> None:
        """
        Distribute requests over testing time
        :param queue: Queue for requests
        """
        requests_per_batch = max(1, self.config.rps // 10)
        batch_interval = 1.0 / (self.config.rps / requests_per_batch)

        request_id = 0
        end_time = self.start_time + self.config.test_time

        while time.time() < end_time and request_id < self.config.total_requests:
            batch_start = time.time()

            for _ in range(requests_per_batch):
                if request_id < self.config.total_requests:
                    await queue.put(request_id)
                    request_id += 1

            batch_end = time.time()
            sleep_time = batch_interval - (batch_end - batch_start)
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)


    async def _stop_workers(
            self,
            queue: asyncio.Queue,
            workers: list[asyncio.Task]
    ) -> None:
        """
        Stop working processes
        :param queue: Queue of tasks
        :param workers: List of tasks
        """
        for _ in workers:
            await queue.put(None)

        await asyncio.gather(*workers, return_exceptions = True)


    def _print_test_info(self) -> None:
        """
        Print info about test start
        """
        print(f"Starting load test...")
        print(f"Target URL: {self.config.url}")
        print(f"Test duration: {self.config.test_time}s, RPS: {self.config.rps} "
              f"(total {self.config.total_requests} requests)")
        print(f"Timeout for responses: {self.config.wait_timeout}s")
        print("-" * 50)

