#!/usr/bin/env python
import os

from setuptools import setup

setup(
    name="maxwidgets",
    version="0.9.7",
    description="A collection of reusable Taurus widgets",
    author="KITS controls",
    author_email="kits-sw@maxiv.lu.se",
    license="GPLv3",
    url="http://www.maxiv.lu.se",
    packages=['maxwidgets.input',
              'maxwidgets.display',
              'maxwidgets.panel',
              'maxwidgets.extra_guiqwt',
              'maxwidgets.extra_guiqwt.ui'],
    package_dir = {'maxwidgets': 'src'},
    install_requires=["taurus"],
    data_files = [('/etc/profile.d/', ['maxwidgets.sh'])]
)
