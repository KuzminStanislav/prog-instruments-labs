from typing import Counter

from test_statistics import TestStatistics, format_status_code


class ResultPrinter:
    @staticmethod
    def print_results(config, statistics: TestStatistics) -> None:
        """
        Print test results
        :param config: Test config
        :param statistics: Test statistics
        """
        summary = statistics.get_request_summary()
        time_stats = statistics.get_response_time_stats()
        status_distribution = statistics.get_status_code_distribution()

        print("\n" + "=" * 40)
        print("LOAD TEST RESULTS")
        print("=" * 40)

        ResultPrinter._print_request_summary(summary)
        ResultPrinter._print_response_times(time_stats)
        ResultPrinter._print_status_distribution(status_distribution)


    @staticmethod
    def _print_request_summary(summary: dict[str, int]) -> None:
        """
        Print summary
        :param summary: Request summary
        """
        print(f"\n=== Request Summary ===")
        print(f"Total requests sent: {summary['total_requests']}")
        print(f"Completed successfully: {summary['completed_successfully']}")
        print(f"Failed requests: {summary['failed_requests']}")
        print(f"- Timeout errors: {summary['timeout_errors']}")
        print(f"- Connection errors: {summary['connection_errors']}")
        print(f"- HTTP errors (5xx): {summary['http_errors_5xx']}")


    @staticmethod
    def _print_response_times(time_stats: dict[str, float]) -> None:
        """
        Print time statistics
        :param time_stats: Time statistics
        """
        print(f"\n=== Response Time (ms) ===")
        print(f"Min: {time_stats['min']:.1f}")
        print(f"Max: {time_stats['max']:.1f}")
        print(f"Mean: {time_stats['mean']:.1f}")
        print(f"Median: {time_stats['median']:.1f}")
        print(f"p75: {time_stats['p75']:.1f}")
        print(f"p90: {time_stats['p90']:.1f}")
        print(f"p95: {time_stats['p95']:.1f}")
        print(f"p99: {time_stats['p99']:.1f}")


    @staticmethod
    def _print_status_distribution(status_distribution: Counter) -> None:
        """
        Print status distribution
        :param status_distribution: Status distribution
        """
        for code, count in status_distribution.most_common():
            formatted_code = format_status_code(code)
            print(f"{formatted_code}: {count}")