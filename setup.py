from distutils.core import setup
from setuptools import find_packages
setup(
    name = 'pydip',
    packages = find_packages(exclude=['pydip.test', 'pydip.test.*']),
    version = '0.1.8',
    description = 'Adjudication logic engine for Diplomacy board game',
    author = 'Aric Parkinson',
    author_email = 'aric.parkinson@gmail.com',
    url = 'https://github.com/aparkins/pydip',
    download_url = 'https://github.com/aparkins/pydip/tarball/0.1.6',
    keywords = ['diplomacy', 'adjudication', 'adjudicator', 'board', 'game'],
    classifiers = [],
    tests_require = ['pytest'],
)
