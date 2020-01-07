#!/usr/bin/env python3
# thoth-python
# Copyright(C) 2018, 2019 Fridolin Pokorny
#
# This program is free software: you can redistribute it and / or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
# type: ignore

"""Tests for Pipfile and Pipfile.lock handling."""

import os

import pytest
import toml

from thoth.python import Pipfile
from thoth.python import PipfileLock
from thoth.python import PackageVersion
from thoth.python import Source

from .base import PythonTestCase


class TestPipfile(PythonTestCase):

    @pytest.mark.parametrize("pipfile", [
        'Pipfile_test1',
    ])
    def test_from_string(self, pipfile: str):
        with open(os.path.join(self.data_dir, 'pipfiles', pipfile), 'r') as pipfile_file:
            content = pipfile_file.read()

        instance = Pipfile.from_string(content)
        # Sometimes toml does not preserve inline tables causing to_string() fail. However, we produce valid toml.
        assert instance.to_dict() == toml.loads(content)

    def test_pipfile_extras_parsing(self):
        instance = Pipfile.from_file(os.path.join(self.data_dir, "pipfiles", "Pipfile_extras"))
        assert instance is not None
        assert len(instance.packages.packages) == 1
        assert "selinon" in instance.packages.packages
        package_version = instance.packages.packages["selinon"]
        assert set(package_version.to_dict().pop("extras")) == {
            "celery",
            "mongodb",
            "postgresql",
            "redis",
            "s3",
            "sentry",
        }
        assert set(package_version.extras) == {"celery", "mongodb", "postgresql", "redis", "s3", "sentry"}

    def test_construct_requirements(self):
        pipfile = Pipfile.from_file(os.path.join(self.data_dir, 'pipfiles', 'Pipfile_requirements'))
        expected = """#
# This file is autogenerated by Thoth and is meant to be used with pip-compile
# as provided by pip-tools.
#
-i https://pypi.python.org/simple
-i https://tensorflow.pypi.thoth-station.ninja/index/manylinux2010/AVX2/simple/

attrs>=10
connexion[swagger-ui]>=1.2; python_version < '2.7.9' or (python_version >= '3.0' and python_version < '3.4')
flask==1.1.1
aiocontextvars
sentry-sdk[flask]
tensorflow==1.13.2

#
# dev packages
#
pytest
"""
        assert pipfile.construct_requirements_in() == expected
        assert pipfile.construct_requirements_txt() == expected


class TestPipfileLock(PythonTestCase):

    @pytest.mark.parametrize("pipfile_lock", [
        'Pipfile_test1.lock',
    ])
    def test_from_string(self, pipfile_lock: str):
        with open(os.path.join(self.data_dir, 'pipfiles', pipfile_lock), 'r') as pipfile_lock_file:
            content = pipfile_lock_file.read()

        with open(os.path.join(self.data_dir, 'pipfiles', pipfile_lock[:-len('.lock')]), 'r') as pipfile_file:
            pipfile_content = pipfile_file.read()

        pipfile_instance = Pipfile.from_string(pipfile_content)
        instance = PipfileLock.from_string(content, pipfile=pipfile_instance)
        assert instance.to_string() == content

    def test_extras_parsing(self):
        pipfile_instance = Pipfile.from_file(os.path.join(self.data_dir, "pipfiles", "Pipfile_extras"))
        instance = PipfileLock.from_file(
            os.path.join(self.data_dir, "pipfiles", "Pipfile_extras.lock"),
            pipfile=pipfile_instance
        )

        assert instance is not None
        assert len(instance.packages.packages) == 34
        assert "selinon" in instance.packages.packages
        package_version = instance.packages.packages["selinon"]
        assert set(package_version.to_dict().pop("extras")) == {
            "celery",
            "mongodb",
            "postgresql",
            "redis",
            "s3",
            "sentry",
        }
        assert set(package_version.extras) == {"celery", "mongodb", "postgresql", "redis", "s3", "sentry"}

    def test_construct_requirements_txt(self):
        pipfile_lock = PipfileLock.from_file(os.path.join(self.data_dir, 'pipfiles', 'Pipfile_requirements.lock'))
        assert pipfile_lock.construct_requirements_txt() == """#
# This file is autogenerated by Thoth and is meant to be used with pip-compile
# as provided by pip-tools.
#
-i https://pypi.python.org/simple
-i https://index-aicoe.a3c1.starter-us-west-1.openshiftapps.com/fedora28/1.9/jemalloc

absl-py==0.5.0 \\
    --hash=sha256:6fcc3c04dc881fd93d793674a42ee8c73155570eda8f8b90c4477c8522478b7b
click==6.6 \\
    --hash=sha256:cc6a19da8ebff6e7074f731447ef7e112bd23adf3de5c597cf9989f2fd8defe9 \\
    --hash=sha256:fcf697e1fd4b567d817c69dab10a4035937fe6af175c05fd6806b69f74cbc6c4
python-dateutil==2.7.3; python_version >= '2.7' \\
    --hash=sha256:1adb80e7a782c12e52ef9a8182bebeb73f1d7e24e374397af06fb4956c8dc5c0 \\
    --hash=sha256:e27001de32f627c22380a688bcc43ce83504a7bc5da472209b4c70f02829f0b8
tensorflow==1.9.0rc0 \\
    --hash=sha256:0588ac4f2b2e3994a5245c9be13a58e6128c26f7e6eb61c2ef90d82b58b78d4c \\
    --hash=sha256:1a83b8e789a5b9bfdfc671d4368b976a8d9cc5d217209264cc987885ff55a6b1 \\
    --hash=sha256:4dedb5dacd20df1e545835a40ad6b337fda11e32432bd643e4a8cd484d72fe0a

#
# dev packages
#
autopep8==1.4 \\
    --hash=sha256:655e3ee8b4545be6cfed18985f581ee9ecc74a232550ee46e9797b6fbf4f336d
"""
