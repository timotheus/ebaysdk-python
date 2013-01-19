#!/usr/bin/env python

#from distutils.core import setup

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from setuptools import setup, find_packages
import re, os

PKG = 'ebaysdk'

# Get the version
VERSIONFILE = os.path.join(PKG, "_version.py")
version = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
        open(VERSIONFILE, "rt").read(), re.M).group(1)


long_desc = """This SDK cuts development time and simplifies tasks like 
error handling and enables you to make Finding, Shopping, Merchandising, 
and Trading API calls. In Addition, the SDK comes with RSS and 
HTML back-end libraries."""

setup(
    name=PKG,
    version=version,
    description="Simple and Extensible eBay SDK for Python",
    author="Tim Keefer",
    author_email="tkeefer@gmail.com",
    url="https://github.com/timotheus/ebaysdk-python",
    license="Apache Software License",
    packages=find_packages(),
    provides=[PKG],
    install_requires=['PyYaml', 'pycurl', 'Beautifulsoup'],
    test_suite='tests',
    long_description=long_desc,
    classifiers=[
      'Topic :: Internet :: WWW/HTTP',
      'Intended Audience :: Developers',
    ]
)
