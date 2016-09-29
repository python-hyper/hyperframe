#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import sys
import platform

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
from distutils.cmd import Command

# Get the version
version_regex = r'__version__ = ["\']([^"\']*)["\']'
with open('hyperframe/__init__.py', 'r') as f:
    text = f.read()
    match = re.search(version_regex, text)

    if match:
        version = match.group(1)
    else:
        raise RuntimeError("No version number found!")

# Stealing this from Kenneth Reitz
if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()


class BenchmarkCommand(Command):
    description = "Run all the benchmarks for hyperframe."
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            import importlib
        except ImportError:
            print("The module 'importlib' is required to run benchmarks.")
            sys.exit(1)

        print("Benchmarking System: {} {}".format(
            platform.system(),
            platform.processor()
        ))
        print("Benchmarking Python: {} {}".format(
            platform.python_implementation(),
            platform.python_version()
        ))
        print("")

        benchmark_directory = os.path.join(os.path.realpath(os.path.dirname(os.path.abspath(__file__))), "bench")
        benchmarks = []
        for module in os.listdir(benchmark_directory):
            if module.endswith(".py"):
                module = importlib.import_module("bench." + module[:-3])
                for bench_class in dir(module):
                    if not bench_class.startswith("_") and bench_class.endswith("Benchmark"):
                        try:
                            benchmark = getattr(module, bench_class)()
                            benchmarks.append(benchmark)
                        except Exception:
                            pass

        print("Collected {} benchmarks to run".format(len(benchmarks)))
        print("")

        for benchmark in sorted(benchmarks, key=lambda x: x.name):
            benchmark.run()


packages = ['hyperframe']

setup(
    name='hyperframe',
    version=version,
    description='HTTP/2 framing layer for Python',
    long_description=open('README.rst').read() + '\n\n' + open('HISTORY.rst').read(),
    author='Cory Benfield',
    author_email='cory@lukasa.co.uk',
    url='http://hyper.rtfd.org',
    packages=packages,
    package_data={'': ['LICENSE', 'README.rst', 'CONTRIBUTORS.rst', 'HISTORY.rst']},
    package_dir={'hyperframe': 'hyperframe'},
    include_package_data=True,
    license='MIT License',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
    cmdclass={
        "bench": BenchmarkCommand
    }
)
