from collections import Counter
from typing import Optional, Union
import statistics

from test_config import RequestResult


class TestStatistics:
    """
    Statistics of load test
    """
    def __init__(self, results: list[RequestResult]):
        """
        Class init
        :param results: List of requests
        """
        self.results = results
        self._response_times = Optional[list[float]] = None


    def response_times(self) -> list[float]:
        """
        Response time of requests
        :return: Time list
        """
        if self._response_times is None:
            self._response_times = [
                r.response_time for r in self.results 
                if r.error is None and 200 <= r.status_code < 400
            ]
        return self._response_times
    

    def get_request_summary(self) -> dict[str, int]:
        """
        Request summary
        :return: Dict of requests
        """
        total = len(self.results)
        completed = len(self.response_times)
        failed = total - completed
        
        timeout_errors = sum(1 for r in self.results if r.error == 'timeout')
        connection_errors = sum(1 for r in self.results if r.error == 'connection')
        http_errors_5xx = sum(1 for r in self.results 
                             if isinstance(r.status_code, int) and r.status_code >= 500)
        
        return {
            'total_requests': total,
            'completed_successfully': completed,
            'failed_requests': failed,
            'timeout_errors': timeout_errors,
            'connection_errors': connection_errors,
            'http_errors_5xx': http_errors_5xx
        }
    

    def get_response_time_stats(self) -> dict[str, float]:
        """
        Statistics of response time
        :return: Dict with time of response
        """
        response_times = self.response_times

        if not response_times:
            return {
                'min': 0.0,
                'max': 0.0,
                'mean': 0.0,
                'median': 0.0,
                'p75': 0.0,
                'p90': 0.0,
                'p95': 0.0,
                'p99': 0.0
            }
        
        sorted_times = sorted(response_times)
        n = len(sorted_times)

        return {
            'min': min(response_times),
            'max': max(response_times),
            'mean': statistics.mean(response_times),
            'median': statistics.median(response_times),
            'p75': sorted_times[int(0.75 * n) - 1] if n > 0 else 0.0,
            'p90': sorted_times[int(0.90 * n) - 1] if n > 0 else 0.0,
            'p95': sorted_times[int(0.95 * n) - 1] if n > 0 else 0.0,
            'p99': sorted_times[int(0.99 * n) - 1] if n > 0 else 0.0,
        }
    

    def get_status_code_distribution(self) -> Counter:
        """
        Distribution of status code
        :return: Counter of status code
        """
        return Counter(r.status_code for r in self.results)
    

    def get_detailed_errors(self) -> dict[str, int]:
        """
        Detailed information about errors
        :return: Dict with errors
        """
        errors = Counter()
        for result in self.results:
            if result.error:
                errors[result.error] += 1
            elif isinstance(result.status_code, int) and result.status_code >= 400:
                errors[f'http_{result.status_code}'] += 1
        
        return dict(errors)
    

def format_status_code(code: Union[int, str]) -> str:
    """
    Format status code
    :param code: Status code
    :return: Formated status code
    """
    match code:
        case 200:
            return "200 OK"
        case 301:
            return "301 Redirect"
        case 302:
            return "302 Redirect"
        case 404:
            return "404 Not Found"
        case 500:
            return "500 Server Err"
        case 'TIMEOUT':
            return "Timeouts"
        case 'CONNECTION_ERROR':
            return "Connection Errors"
        case 'OTHER_ERROR':
            return "Other Errors"
        case int(code) if 400 <= code < 500:
            return f"{code} Client Error"
        case int(code) if 500 <= code < 600:
            return f"{code} Server Error"
        case _:
            return str(code)

