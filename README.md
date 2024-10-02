# robotframework-stopwatch
![Version](https://img.shields.io/badge/version-0.2.9-%2392C444)

Robot Framework listener extension for agile perfomance testing.

Evaluate test case execution against its statistical average run time & user-configured timedelta in.

## Why?
While Robot Framework does provide an ability to setup time limits (e.g. timeouts) as a means of failing tests/suites depending on their time of execution, such approach is somewhat set in stone. Meaning that you have to manually inspect runtimes of your tests and decide upon much needed time limits. When you have single master suite, or your testing production is not quite large - this works alright. But when your number of tests is 300+, managing each timeout individually is rather straining. Add to that multiple layers of configurations such as different environments, testing tools, or downright infrastructure inconsistencies that do occur and you end up quite strained with the idea of reliable perfomance testing. **This extension is an attempt to provide a reliable tool for flexible, integrated perfomance testing.**

## Overview
As mentioned above, *robotframework-stopwatch is not quite a library, but extension of built-in Robot Framework Listener.*

When first integrated, the ``StopwatchListener`` will initialise an empty logfile (by default: ``./stopwatch_log.json``) to store required run data for every individual test. After first run, taking into consideration the test succeeded, average runtime for this test will be set to this run time of execution. Afterwards, each succesful test runtime will be used to update the last average runtime value for the test. The user-preconfigured ``timedelta`` is then used to evaluate all future test runs status. Failed tests, whether due to timedelta exceeded or natural test fails, have no effect upon test average runtime. Extension also provides a log data divider ``environment`` to catalog same tests based on different setups.

When test with established average runtime fails due to exceeded time limit, test is marked as failed with a following message output:

```shell
Stopwatch! Test runtime exceeded the acceptable time limit.
```

## Installation

```shell
pip install robotframework-stopwatch
```

## Usage
**robotframework-stopwatch** relies on a single base class ``StopwatchListener``, that comes with following attributes:

- ``logfile (str)``: The path to the log file. By default: ``./stopwatch_log.json``

- ``environment (str, optional)`` The marker/divider used to separate test run data across different configurations.

- ``timedelta (str, optional)``: The time delta value used for evaluating test runtimes.
            Defaults to ``"10s"``. Time formats include: ``"5s"``, ``"2 min"``, ``"1 hour"``.

There are two ways to implement robotframework-stopwatch.

#### Listener approach
When custom listener is already in-use, *or robotframework-stopwatch is needed on a global level* (every suite, every test), create or modify the listener:

```python
from robot.stopwatch import StopwatchListener

class CustomListener(StopwatchListener):
    def __init__(self, logfile, environment, timedelta):
```

This won't interfere with your custon listener functionality.

#### Command-line approach
When there is a need to set separate timedelta for different suites/tests, or setting up a listener is not required, it is possible to pass ``StopwatchListener`` and its command line arguments directly from terminal:

```shell
robot --listener robot.stopwatch.StopwatchListener:"logfile":"environment":"timedelta" some_test.robot
```
### Concurecy

As of now, robotframework-stopwatch supports concurent read/write, making it possible to share a logfile data among multiple agents, instances, test runners. To incorporate concurent logging do rely on the most suitable tactics of shared file storage for your organisation (e.g. Azure Shared Storage).

## Plans
1. Interface for setting up test run data log in a remote database. 
2. Robust ``timedelta`` time formats.
3. Robust ``logfile`` handling.
