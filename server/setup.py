#!/usr/bin/env python3

from distutils.core import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(name='CloudBurstServer',
      version='0.1',
      description='CloudBurst server',
      author='Angus Trau',
      author_email='contact@angus.ws',
      url='https://gitlab.erc.monash.edu.au/hpc-team/cloudburst',
      packages=['CloudBurstServer'],
      scripts=['scripts/cloudburstd'],
      install_requires=required,
     )
