import json
import os

import portalocker
from robot import result, running
from robot.api import logger
from robot.api.interfaces import ListenerV3

class StopwatchListener(ListenerV3):
    """
    The robotframework-stopwatch listener base class.

    Attributes:
        logfile (str): The path to the log file. By default: ``./stopwatch_log.json``
        
        environment (str, optional): The marker/divider used to separate test run data 
            across different configurations.

        timedelta (str, optional): The time delta value used for evaluating test runtimes.
            Defaults to ``"10s"``. Time formats include: ``"5s"``, ``"2 min"``, ``"1 hour"``.
    """

    ROBOT_LISTENER_API_VERSION = 3
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self, logfile: str = "./stopwatch_log.json", environment: str = "", timedelta: str = "") -> None:
        self.logfile: str = self._init_logfile(logfile)
        self.environment: str = self._init_environment(environment)
        self.timedelta: int = self._init_timedelta(timedelta)
        self.log_data: dict = self._init_log_data()
        self.test: str
        self.test_run_data: dict
        self.test_average_runtime: int
        self.test_runtime_log: list

    def _init_logfile(self, logfile) -> str:
        if logfile:
            return os.path.abspath(logfile)
        else:
            if not os.path.exists("./stopwatch_log.json"):
                logger.console("==============================================================================\n"
                               "Stopwatch: Log file is set to default location: ./stopwatch_log.json\n"
                               "==============================================================================")
            return os.path.abspath("./stopwatch_log.json")

    def _init_timedelta(self, timedelta) -> int:
        if timedelta:
            digits = []
            for char in timedelta:
                if char.isdigit():
                    digits.append(char)
                else:
                    break
            time_value = int("".join(digit for digit in digits))
            if "h" in timedelta:
                return time_value * 60 * 60
            elif "m" in timedelta:
                return time_value * 60
            else:
                return time_value
        else:
            return 10

    def _init_environment(self, environment) -> str:
        return environment.lower() if environment else "main"

    def _init_log_data(self) -> dict:
        data_json = {}
        if os.path.exists(self.logfile):
            with open(self.logfile, "r") as stopwatch_log:
                portalocker.lock(stopwatch_log, portalocker.LOCK_SH)
                try:
                    data_json = json.load(stopwatch_log)
                except json.JSONDecodeError as e:
                    print(f"Error loading JSON file: {e}")
                    os.remove(self.logfile)
                finally:
                    portalocker.unlock(stopwatch_log)
        else:
            os.makedirs(os.path.dirname(self.logfile), exist_ok=True)
            with open(self.logfile, "x") as stopwatch_log:
                json.dump(data_json, stopwatch_log)
        return data_json

    def start_test(self, data: running.TestCase, result: result.TestCase):
        def _initialise_test_data(self, result) -> None:
            self.test = str(result.name)
            if self.test not in self.log_data:
                self.log_data[self.test] = {}
            if self.environment not in self.log_data[self.test]:
                self.log_data[self.test][self.environment] = {
                    "average_runtime": 0,
                    "runtime_log": []
                }
            self.test_average_runtime = self.log_data[self.test][self.environment]["average_runtime"]
            self.test_runtime_log = self.log_data[self.test][self.environment]["runtime_log"]

        _initialise_test_data(self, result)

    def end_test(self, data: running.TestCase, result: result.TestCase):
        def _parse_test_run_data(self) -> None:
            self.test_run_data = {
                "id": result.start_time.strftime("%d%m%y_%H%M%S") if result.start_time else "",
                "runtime": result.elapsed_time.seconds,
                "passed": result.passed,
                "delta_ok": None
            }

        def _evaluate_test_by_delta(self) -> None:
            if not self.test_average_runtime:
                return
            if self.test_run_data["passed"]: 
                if self.test_run_data["runtime"] > self.test_average_runtime + self.timedelta:
                    self.test_run_data["delta_ok"] = False
                    result.passed = False
                    result.message = "\033[91m        Stopwatch! Test runtime exceeded the acceptable time limit.\033[0m"
                else:
                    self.test_run_data["delta_ok"] = True

        def _queue_test_run_data(self) -> None:
            if self.test_average_runtime:
                if self.test_run_data["passed"] and self.test_run_data["delta_ok"]:
                    self.test_average_runtime = (self.test_run_data["runtime"] + self.test_average_runtime) // 2
            else:
                    self.test_average_runtime = self.test_run_data["runtime"]
            self.log_data[self.test][self.environment]["average_runtime"] = self.test_average_runtime
            self.test_runtime_log.insert(0, self.test_run_data)

        _parse_test_run_data(self)
        _evaluate_test_by_delta(self)
        _queue_test_run_data(self)
    
    def end_suite(self, data: running.TestSuite, result: result.TestSuite):
        def _write_tests_runs_data_(self) -> None:
            with open(self.logfile, "w") as stopwatch_log:
                portalocker.lock(stopwatch_log, portalocker.LOCK_EX)
                try:
                    json.dump(self.log_data, stopwatch_log, indent=4)
                finally:
                    portalocker.unlock(stopwatch_log)

        _write_tests_runs_data_(self)
