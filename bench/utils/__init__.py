import struct
import sys
import time
import random

_RANDOM = random.Random(0)
_SECTIONS = 10


class _BaseBenchmark(object):
    def __init__(self, name, ticks):
        self.name = name
        self.start_time = 0
        self.end_time = 0
        self.duration = 0
        self.variance = 0.0
        self._sections = []
        self._watch = 0
        self._ticks = ticks
        self._ticked = 0

    def dot(self):
        sys.stdout.write(".")
        sys.stdout.flush()

    def start_watch(self):
        self._watch = time.time()

    def stop_watch(self):
        stop = time.time()
        self.duration += stop - self._watch
        self._watch = 0

        # Keep track of section ticks.
        self._ticked += 1
        if self._ticked % (self._ticks // _SECTIONS) == 0:
            self._sections.append(self.duration)
            self.dot()

    def run(self):
        sys.stdout.write(self.name + " ")
        sys.stdout.flush()
        self.setup()
        self.dot()

        self.benchmark()

        # Calculate the total variance between each section.
        section_durations = []
        for i in range(1, len(self._sections)):
                section_durations.append(self._sections[i] - self._sections[i - 1])
        average_time = sum(section_durations) / len(section_durations)
        self.variance = sum([abs(average_time - dur) for dur in section_durations]) / 2

        result = " {0:.2f} ms +/- {1:.2f} ms\n".format(
            self.duration * 1000,
            self.variance * 1000
        )

        sys.stdout.write("." * (79 - len(result) - len(self.name) - _SECTIONS))
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
