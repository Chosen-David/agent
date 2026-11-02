#!/usr/bin/env python3
"""Run the standard unittest CLI with bounded execution diagnostics on stderr."""
import json
import os
from pathlib import Path
import platform
import sys
import time
import unittest


class TelemetryResult(unittest.TextTestResult):
    def _emit(self, event, **fields):
        self.stream.writeln("\nCI_TEST " + json.dumps(
            {"event": event, **fields}, ensure_ascii=True, sort_keys=True))
        self.stream.flush()

    def startTest(self, test):
        self._started = (time.perf_counter(), time.process_time())
        self._emit("start", test=test.id())
        super().startTest(test)

    def stopTest(self, test):
        wall, cpu = self._started
        super().stopTest(test)
        self._emit("finish", test=test.id(),
                   wall_seconds=time.perf_counter() - wall,
                   process_cpu_seconds=time.process_time() - cpu)


class TelemetryRunner(unittest.TextTestRunner):
    resultclass = TelemetryResult


def main(argv=None):
    sys.path[:0] = [os.getcwd(), str(Path(__file__).resolve().parents[1])]
    print("CI_TEST " + json.dumps({
        "event": "run", "python": sys.version, "platform": platform.platform(),
        "pid": os.getpid(), "stack_sampling": "not enabled",
        "scope": "wall includes setup/body/cleanup; CPU excludes child processes; no IO counters",
    }, ensure_ascii=True, sort_keys=True), file=sys.stderr, flush=True)
    unittest.main(module=None, argv=argv, testRunner=TelemetryRunner)


if __name__ == "__main__":
    main()
