#!/usr/bin/env python

from setuptools import setup
from glob import glob

vfile = 'lib/dmr/version.py'
try:
    # python 2
    execfile(vfile)
except NameError:
    # py3k
    exec(compile(open(vfile).read(), vfile, 'exec'))


setup(name="dmr",
      version=__version__,
      description="dmr: Deduplicate my resume",
      author="Chris St. Pierre",
      author_email="chris.a.st.pierre@gmail.com",
      # nosetests
      test_suite='nose.collector',
      packages=["dmr",
                "dmr.output"
                ],
      install_requires=['genshi', 'argparse'],
      tests_require=['nose', 'pylint', 'pep8'],
      package_dir={'': 'lib', },
      scripts=glob('bin/*'),
      data_files=[('share/dmr/templates', glob('templates/*'))]
      )
