import os
import struct
import sys
import time
import random
import warnings

# Seed was randomly generated with 128 bytes of entropy because old Python
# versions have low initial entropy when seeds have too many NULL bytes.
_SEED = open(os.path.join(os.path.dirname(__file__), "seed"), "rb").read()
_RANDOM = random.Random(_SEED)
_SECTIONS = 10

# The best time taking function for benchmarking is monotonic time. This
# option was not available in older versions of Python and a backfill
# module was created for that purpose. If the module is not available,
# a warning is emitted and an alternative time is used.
if hasattr(time, "monotonic"):
    monotime = time.monotonic
else:
    try:
        import monotonic
        monotime = monotonic.monotonic
    except ImportError:
        warnings.warn("Using an non-monotonic clock for benchmarks. "
                      "Consider installing monotonic module from pip.")

        if hasattr(time, "perf_counter"):
            monotime = time.perf_counter
        else:
            monotime = time.time


class _BaseBenchmark(object):
    def __init__(self, name, rounds):
        if rounds % _SECTIONS:
            raise ValueError("Rounds should always be a multiple of {}.".format(_SECTIONS))

        self.name = name
        self.start_time = 0
        self.end_time = 0
        self.duration = 0
        self.variance = 0.0
        self._sections = []
        self._watch = 0
        self.rounds = rounds
        self._ticked = 0

    def dot(self):
        sys.stdout.write(".")
        sys.stdout.flush()

    def start_watch(self):
        self._watch = monotime()

    def stop_watch(self):
        stop = monotime()
        self.duration += stop - self._watch
        self._watch = 0

        # Keep track of section ticks.
        self._ticked += 1
        if self._ticked % (self.rounds // _SECTIONS) == 0:
            self._sections.append(self.duration)
            self.dot()

    def run(self):
        sys.stdout.write(self.name + " ")
        sys.stdout.flush()
        self.setup()
        self.dot()

        # All calls to start/stop_watch should be in this function.
        self.benchmark()

        # Calculate the total variance between each section.
        section_durations = []
        for i in range(1, len(self._sections)):
                section_durations.append(self._sections[i] - self._sections[i - 1])
        average_time = sum(section_durations) / len(section_durations)
        self.variance = sum([abs(average_time - dur) for dur in section_durations]) / 2

        result = "{0:.2f} ms".format(self.duration * 1000)
        result = "." * (15 - len(result)) + " " + result
        result += " +/- {0:.2f} ms\n".format(
            self.variance * 1000
        )

        sys.stdout.write("." * (40 - len(self.name) - _SECTIONS))
        sys.stdout.write(result)
        sys.stdout.flush()

        self.cleanup()

    def setup(self):
        raise NotImplementedError("_BaseBenchmark.setup() is not implemented.")

    def benchmark(self):
        raise NotImplementedError("_BaseBenchmark.setup() is not implemented.")

    def cleanup(self):
        raise NotImplementedError("_BaseBenchmark.setup() is not implemented.")


def get_bool():
    return True if get_int(0, 1) == 1 else False


def get_int(l, h):
    return _RANDOM.randint(l, h)


def get_bytes(n):
    return b''.join([struct.pack("@B", _RANDOM.randint(0, 255)) for _ in range(n)])
