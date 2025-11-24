import sys

import asyncio

from cli import ResultPrinter
from test_config import parse_args
from tester import LoadTester


async def main() -> None:
    try:
        config = parse_args()
        tester = LoadTester(config)
        statistics = await tester.run_load_test()
        ResultPrinter.print_results(config, statistics)

    except ValueError as e:
        print(f"Value error: {e}")
        sys.exit(1)

    except KeyboardInterrupt:
        print("\nTest was inerrupted by the user")
        sys.exit(1)
    
    except Exception as e:
        print(f"Error: {e}")
        #traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())