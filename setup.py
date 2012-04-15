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

#try:
from setuptools import setup, find_packages
#except ImportError:
#  from distutils.core import setup

import sys

execfile('./ebaysdk/__init__.py')
VERSION = __version__

long_desc = """This SDK cuts development time and simplifies tasks like 
error handling and enables you to make Finding, Shopping, Merchandising, 
and Trading API calls. In Addition, the SDK comes with RSS and 
HTML back-end libraries."""

setup(
    name="ebaysdk",
    version=VERSION,
    description="Simple and Extensible eBay SDK for Python",
    author="Tim Keefer",
    author_email="tim@timkeefer.com",
    url="http://code.google.com/p/ebay-sdk-python/",
    license="Apache Software License",
    packages=find_packages(),
    provides=['ebaysdk'],
    install_requires=['BeautifulSoup', 'PyYAML', 'pycurl', 'elementtree'],
    test_suite='tests',
    long_description=long_desc,
    classifiers=[
      'Topic :: Internet :: WWW/HTTP',
      'Intended Audience :: Developers',
    ]     
) 
