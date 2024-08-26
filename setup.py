#  obscreen
#  ---------------
#  A fancy self-hosted digital signage tool. Free, simple and working.
#
#  Author:  jr-k (c) 2024
#  Website: https://github.com/jr-k/obscreen
#  License: GPLv2 (see LICENSE file)

import sys
import logging

from setuptools import setup, find_packages

common_dependencies = [
    'flask==2.3.3',
    'flask-restx==1.3.0',
    'python-dotenv',
    'cron-descriptor',
    'waitress',
    'flask-login',
    'psutil',
    'pysqlite3',
]

if sys.platform == "win32":
    common_dependencies.remove('pysqlite3')

if sys.platform == "darwin":
    common_dependencies.remove('pysqlite3')

setup(
    name='obscreen',
    version=open('version.txt').read(),
    description='A fancy self-hosted digital signage tool. Free, simple and working.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='JRK',
    author_email='jrk@jierka.com',
    url='https://github.com/jr-k/obscreen',
    packages=find_packages(),
    platforms='any',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: OS Independent',
        'Topic :: Desktop Environment :: Screen Savers',
        'Topic :: Multimedia :: Graphics'
    ],
    python_requires='>=3.6',
    install_requires=common_dependencies,
)
