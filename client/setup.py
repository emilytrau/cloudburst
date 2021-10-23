#!/usr/bin/env python3

from distutils.core import setup

setup(name='CloudBurstClient',
      version='0.1',
      description='CloudBurst client tools',
      author='Angus Trau',
      author_email='contact@angus.ws',
      url='https://gitlab.erc.monash.edu.au/hpc-team/cloudburst',
      packages=['CloudBurstClient'],
      scripts=['scripts/CloudBurstResume', 'scripts/CloudBurstResumeFail', 'scripts/CloudBurstSuspend'],
      install_requires=['requests', 'pyslurm'],
     )
