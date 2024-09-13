import json
import os

from robot import result, running
from robot.api.interfaces import ListenerV3

class Stopwatch(ListenerV3):

    ROBOT_LISTENER_API_VERSION = 3
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self, logfile: str ="./stopwatch_history.json", timedelta: str = "60 seconds") -> None:
        self.logfile: str = logfile
        self.timedelta: int = self._get_timedelta(timedelta)
        self.environment: str = self._get_environment()
        self.history_json: dict = self._get_history()
        self.test: str
        self.test_average_runtime: int
        self.test_run_data: dict
        self.test_runtime_log: list

    def _get_timedelta(self, timedelta) -> int:
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

    def _get_environment(self) -> str:
        environment = os.getenv("DevEnvironment")
        return environment.lower() if environment else "www"

    def _get_history(self) -> dict:
        data_json = {}
        if os.path.exists(self.logfile):
            try:
                with open(self.logfile, "r") as time_log:
                    data_json = json.load(time_log)
            except json.JSONDecodeError as e:
                print(f"Error loading JSON file: {e}")
                os.remove(self.logfile)
        return data_json

    def start_test(self, data: running.TestCase, result: result.TestCase):
        def _initialise_test_data(self, result) -> None:
            self.test = str(result.name)
            if self.test not in self.history_json:
                self.history_json[self.test] = {}
            if self.environment not in self.history_json[self.test]:
                self.history_json[self.test][self.environment] = {
                    "average_runtime": 0,
                    "runtime_log": []
                }
            self.test_average_runtime = self.history_json[self.test][self.environment]["average_runtime"]
            self.test_runtime_log = self.history_json[self.test][self.environment]["runtime_log"]

        _initialise_test_data(self, result)

    def end_test(self, data: running.TestCase, result: result.TestCase):
        def _parse_test_run_data(self) -> None:
            test_run_id = len(self.test_runtime_log)
            test_run_timestamp = result.start_time.strftime("%d/%m/%y %H:%M:%S") if result.start_time else None
            test_run_status = result.passed
            test_runtime = result.elapsed_time.seconds
            self.test_run_data = {
                "id": test_run_id,
                "timestamp": test_run_timestamp,
                "passed": test_run_status,
                "runtime": test_runtime,
                "delta_exceeded": None
            }

        def _evaluate_test_runtime(self) -> None:
            if self.test_average_runtime:
                if self.test_run_data["passed"] and self.test_run_data["runtime"] > self.test_average_runtime + self.timedelta:
                    self.test_run_data["delta_exceeded"] = True
                    result.passed = False
                    result.message = "Stopwatch: PASS, but execution exceeded acceptance time delta."
                else:
                    self.test_run_data["delta_exceeded"] = False

        def _update_test_average_runtime(self) -> None:
            if self.test_run_data["passed"] and not self.test_run_data["delta_exceeded"]:
                if self.test_average_runtime:
                    self.test_average_runtime = (self.test_run_data["runtime"] + self.test_average_runtime) // 2
                else:
                    self.test_average_runtime = self.test_run_data["runtime"]

        def _write_test_run_data(self) -> None:
            self.history_json[self.test][self.environment]["average_runtime"] = self.test_average_runtime
            self.test_runtime_log.insert(0, self.test_run_data)
            with open(self.logfile, "w") as json_file:
                json.dump(self.history_json, json_file, indent=4)

        _parse_test_run_data(self)
        _evaluate_test_runtime(self)
        _update_test_average_runtime(self)
        _write_test_run_data(self)
