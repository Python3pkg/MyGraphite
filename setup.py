#!/usr/bin/env python
import os
from setuptools import setup, find_packages

base = os.path.dirname(os.path.abspath(__file__))

README_PATH = os.path.join(base, "README.rst")

install_requires = []

tests_require = []

setup(name='graphite_package',
      version='0.0.1',
      description='',
      long_description=open(README_PATH).read(),
      author='Test',
      author_email='test',
      url='',
      packages=find_packages(),
      install_requires=install_requires,
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Operating System :: MacOS',
          'Operating System :: POSIX :: Linux',
          'Topic :: System :: Software Distribution',
          'License :: OSI Approved :: Apache Software License 2.0',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
           'Programming Language :: Python :: 2 :: Only'
      ]
)
