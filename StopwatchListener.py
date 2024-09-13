import json
import os

from robot import result, running
from robot.api.interfaces import ListenerV3

class StopwatchListener(ListenerV3):

    ROBOT_LISTENER_API_VERSION = 3
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self, logfile="./robot_history.json") -> None:
        self.environment: str = self._get_environment()
        self.logfile: str = logfile
        self.history: dict = self._get_history()
        self.suite: str

    def _get_environment(self) -> str:
        environment = os.getenv("DevEnvironment")
        return environment.lower() if environment else "www"

    def _get_history(self) -> dict:
        data = {}
        if os.path.exists(self.logfile):
            try:
                with open(self.logfile, "r") as time_log:
                    data = json.load(time_log)
            except json.JSONDecodeError as e:
                print(f"Error loading JSON file: {e}")
                os.remove(self.logfile)
        return data

    def start_suite(self, data: running.TestSuite, result: result.TestSuite):

        def _initialise_suite_data(self, result):
            self.suite = str(result.source).rsplit('/', 1)[1].rstrip('.robot')
            if self.suite not in self.history:
                self.history[self.suite] = {}
            if self.environment not in self.history[self.suite]:
                self.history[self.suite][self.environment] = {
                    "average_elapsed_time": None,
                    "runs": []
                }

        _initialise_suite_data(self, result)

    def end_suite(self, data: running.TestSuite, result: result.TestSuite):

        
        suite_history = self.history[self.suite][self.environment]["runs"]

        run_id = len(suite_history)
        run_timestamp = result.start_time.strftime("%d/%m/%y %H:%M") if result.start_time else None
        run_status = result.passed
        run_elapsed_time = result.elapsed_time.seconds

        suite_run = {
            "id": run_id,
            "timestamp": run_timestamp,
            "status": run_status,
            "elapsed_time": run_elapsed_time
        }

        self.history[self.suite][self.environment]["runs"].insert(0, suite_run)
        with open(self.logfile, "w") as time_log_json:
            json.dump(self.history, time_log_json, indent=4)
