import os
import glob
import copy
from unittest import TestCase
from subprocess import Popen, PIPE, STDOUT

# path to base test directory
testdir = os.path.abspath(os.path.join(os.path.dirname(__file__)))

# path to top-level dmr directory
srcpath = os.path.abspath(os.path.join(testdir, "..", ))

# path to pylint rc file
rcfile = os.path.join(testdir, "pylintrc.conf")


class TestCodeChecks(TestCase):
    def get_env(self):
        env = copy.copy(os.environ)
        if 'PYTHONPATH' in os.environ:
            env['PYTHONPATH'] = '%s:%s' % (env['PYTHONPATH'], testdir)
        else:
            env['PYTHONPATH'] = testdir
        return env

    def get_filelist(self):
        rv = []
        for root, _, files in os.walk(os.path.join(srcpath, "lib")):
            rv.extend(os.path.join(root, f) for f in files
                      if f.endswith(".py"))
        rv.extend(os.path.join(srcpath, "bin", f)
                  for f in glob.glob(os.path.join(srcpath, "bin", "*")))
        return rv

    def test_pylint(self):
        """ Check code for pylint problems """
        args = ["pylint", "--rcfile", rcfile,
                "--init-hook", "import sys;sys.path.append('%s')" %
                os.path.join(srcpath, "lib")] + self.get_filelist()
        print "running: %s" % args
        pylint = Popen(args, stdout=PIPE, stderr=STDOUT, env=self.get_env())
        print(pylint.communicate()[0])
        self.assertEqual(pylint.wait(), 0)

    def test_pep8(self):
        """ Check code for pep8 problems """
        args = ["pep8"] + self.get_filelist()
        print "running: %s" % args
        pep8 = Popen(args, stdout=PIPE, stderr=STDOUT, env=self.get_env())
        print(pep8.communicate()[0])
        self.assertEqual(pep8.wait(), 0)
