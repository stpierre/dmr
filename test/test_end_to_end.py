import os
import copy
import dmr.input
import dmr.config
from unittest import TestCase

# path to base test directory
testdir = os.path.abspath(os.path.join(os.path.dirname(__file__)))


class TestEndToEnd(TestCase):
    """ Perform end-to-end test(s), from input to output.  Currently,
    this only uses the JSON and plaintext output formats, because the
    other formats may depend on the version of docutils and how it
    renders output. Other formats can be added easily.

    To regenerate the expected output, run this module directly as a
    script.
    """

    # base options for all output formats
    options = dict(footer=dmr.config._get_footer())

    # per-output format options
    fmt_options = dict(
        json=dict(pretty=True),
        latex=dict(template_path=os.path.abspath(os.path.join(testdir, '..',
                                                              "templates")),
                   template="latex.genshi"),
        text=dict(template_path=os.path.abspath(os.path.join(testdir, '..',
                                                             "templates")),
                  template="text.genshi"))

    original_config = copy.deepcopy(dmr.config.config)

    def get_expected(self, fmt):
        return open(os.path.join(testdir, "end_to_end.%s" % fmt)).read()

    def get_actual(self, fmt):
        fmt_opts = copy.deepcopy(self.options)
        fmt_opts.update(self.fmt_options.get(fmt, dict()))
        config = dmr.config._get_default_config(fmt, opts=fmt_opts)
        return config.output_class(dmr.input.parse(open(
                    os.path.join(testdir, "end_to_end.rst")))).output()

    def _test_format(self, fmt):
        self.assertEqual(self.get_expected(fmt),
                         self.get_actual(fmt))

    def test_json(self):
        """ End-to-end test with JSON output """
        self._test_format("json")

    def test_text(self):
        """ End-to-end test with JSON output """
        self._test_format("text")


if __name__ == "__main__":
    # update expected test output
    tester = TestEndToEnd("test_json")
    for fmt in ["json", "text"]:
        outfile = os.path.join(testdir, "end_to_end.%s" % fmt)
        print("Writing %s" % outfile)
        open(outfile, "w").write(tester.get_actual(fmt))
