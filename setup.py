"""Setup script.

Run "python3 setup --help-commands" to list all available commands and their
descriptions.
"""
import re
import sys
from abc import abstractmethod
# Disabling checks due to https://github.com/PyCQA/pylint/issues/73
from subprocess import CalledProcessError, call, check_call

from setuptools import Command, find_packages, setup


class SimpleCommand(Command):
    """Make Command implementation simpler."""

    user_options = []

    def __init__(self, *args, **kwargs):
        """Store arguments so it's possible to call other commands later."""
        super().__init__(*args, **kwargs)
        self._args = args
        self._kwargs = kwargs

    @abstractmethod
    def run(self):
        """Run when command is invoked.

        Use *call* instead of *check_call* to ignore failures.
        """

    def initialize_options(self):
        """Set default values for options."""

    def finalize_options(self):
        """Post-process options."""


# pylint: disable=attribute-defined-outside-init, abstract-method
class TestCommand(Command):
    """Test tags decorators."""

    user_options = [
        ("k=", None, "Specify a pytest -k expression."),
    ]

    def get_args(self):
        """Return args to be used in test command."""
        if self.k:
            return f"-k '{self.k}'"
        return ""

    def initialize_options(self):
        """Set default size and type args."""
        self.k = ""

    def finalize_options(self):
        """Post-process."""
        pass


class Cleaner(SimpleCommand):
    """Custom clean command to tidy up the project root."""

    description = 'clean build, dist, pyc and egg from package and docs'

    def run(self):
        """Clean build, dist, pyc and egg from package and docs."""
        call('make clean', shell=True)


class Test(TestCommand):
    """Run all tests."""

    description = "run tests and display results"

    def run(self):
        """Run tests."""
        cmd = f"python3 -m pytest tests/ {self.get_args()}"
        try:
            check_call(cmd, shell=True)
        except CalledProcessError as exc:
            print(exc)
            print('Unit tests failed. Fix the errors above and try again.')
            sys.exit(-1)


class TestCoverage(Test):
    """Display test coverage."""

    description = "run tests and display code coverage"

    def run(self):
        """Run tests quietly and display coverage report."""
        cmd = "python3 -m pytest --cov=. tests/ --cov-report term-missing"
        cmd += f" {self.get_args()}"
        try:
            check_call(cmd, shell=True)
        except CalledProcessError as exc:
            print(exc)
            print('Coverage tests failed. Fix the errors above and try again.')
            sys.exit(-1)


class Linter(SimpleCommand):
    """Code linters."""

    description = 'lint Python source code'

    def run(self):
        """Run yala."""
        print('Yala is running. It may take several seconds...')
        try:
            check_call('yala setup.py tests kytos', shell=True)
            print('No linter error found.')
        except CalledProcessError:
            print('Linter check failed. Fix the error(s) above and try again.')
            sys.exit(-1)


# We are parsing the metadata file as if it was a text file because if we
# import it as a python module, necessarily the kytos.utils module would be
# initialized.
META_FILE = open("kytos/utils/metadata.py").read()
METADATA = dict(re.findall(r"(__[a-z]+__)\s*=\s*'([^']+)'", META_FILE))

setup(name='kytos-utils',
      version=METADATA.get('__version__'),
      description=METADATA.get('__description__'),
      long_description=open("README.rst", "r").read(),
      url=METADATA.get('__url__'),
      author=METADATA.get('__author__'),
      author_email=METADATA.get('__author_email__'),
      license=METADATA.get('__license__'),
      test_suite='tests',
      include_package_data=True,
      scripts=['bin/kytos'],
      install_requires=[line.strip()
                        for line in open("requirements/run.txt").readlines()
                        if not line.startswith('#')],
      extras_require={'dev': [
          'pip-tools >= 2.0',
          'pytest==8.0.1',
          'pytest-cov==4.1.0',
          'pytest-asyncio==0.23.5',
          'black==24.2.0',
          'isort==5.13.2',
          'pylint==3.1.0',
          'pycodestyle==2.11.1',
          'yala==3.2.0',
          'tox==4.13.0',
          'virtualenv==20.25.1',
      ]},
      packages=find_packages(exclude=['tests']),
      cmdclass={
          'clean': Cleaner,
          'coverage': TestCoverage,
          'lint': Linter,
          'test': Test
      },
      zip_safe=False)
