#!/usr/bin/env python

from setuptools import setup, find_packages

version = '0.1dev'

print '''------------------------------
Installing OMdatabase version {}
------------------------------
'''.format(version)

setup(
    name='OMdatabase',
    version=version,
    author='lx Gui',
    author_email='guilixuan@gmail.com',
    keywords=['bioinformatics', 'NGS'],
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    scripts=['scripts/oms_database'],
    install_requires=[
        'pyyaml',
        'HTSeq',
        'gtfparse',
        'ujson',
        'click'
    ],
)

print '''------------------------------
OMdatabase installation complete!
------------------------------
'''
