from typing import Optional, Union

import argparse
from dataclasses import dataclass


class TestConfig:
    """
    Load test config
    """
    def __init__(
            self, url: str, 
            rps: int,
            test_time: int,
            wait_timeout: int
            ):
        """
        Class initialization
        :param url: site URL
        :param rps: number of requests per second
        :param test_time: test duration
        :param wait_timeout: Timeout after test ending
        """
        self.url = url
        self.rps = rps
        self.test_time = test_time
        self.wait_timeout = wait_timeout


    @property
    def total_requests(self) -> int:
        """
        Total requests of test
        """
        return self.rps * self.test_time
    

    def __str__(self) -> str:
        """
        Config(str)
        """
        return (f"TestConfig(url = '{self.url}', rps = {self.rps}, "
                f"test_time = {self.test_time}, wait_timeout = {self.wait_timeout}, "
                f"total_requests = {self.total_requests})")
    

class RequestResult:
    """
    Result of 1 HTTP request
    :param request_id: id of request
    :param status_code: HTTP status code or error
    :param response_time: time of answer
    :param error: description of error 
    """
    def __init__(
            self,
            request_id: int,
            status_code: Union[int, str],
            response_time: float,
            error: Optional[str] = None
        ):
        self.request_id = request_id
        self.status_code = status_code
        self.response_time = response_time
        self.error = error


def parse_args() -> TestConfig:
    """
    Arguments parsing
    :return: Test Config
    """
    parser = argparse.ArgumentParser(
        description = "Site load test",
        formatter_class = argparse.RawDescriptionHelpFormatter,
        epilog = """
        Examples:
        python main.py https://www.bitrix24.ru/prices/ 100 10 5
        """
    )

    parser.add_argument(
        'url',
        help = 'Site URL' 
    )
    parser.add_argument(
        'rps',
        type=int,
        help='RPS'
    )
    parser.add_argument(
        'test_time',
        type=int, 
        help='Test duratiom'
    )
    parser.add_argument(
        'wait_timeout',
        type=int,
        help='Timeout after test ending'
    )

    args = parser.parse_args()

    if args.rps <= 0:
        raise ValueError("RPS must be > 0")
    if args.test_time <= 0:
        raise ValueError("Test time must be > 0")
    if args.wait_timeout <= 0:
        raise ValueError("Timeout must be > 0")
    
    return TestConfig(
    url=args.url,
    rps=args.rps,
    test_time=args.test_time,
    wait_timeout=args.wait_timeout
)

