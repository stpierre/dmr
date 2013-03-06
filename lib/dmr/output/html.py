""" This module provides a dmr output format to write HTML output
using the :mod:`docutils` HTML translator.

This is the default output format.  Because a dmr document is already
structured to look like a resume, this just uses the default docutils
HTML translator -- it's basically equivalent to running ``rst2html``
on your reST resume.
"""

import copy
from dmr.config import config
from dmr.output.base import BaseOutput
from docutils.writers.html4css1 import Writer
from docutils.io import StringOutput
from docutils.frontend import OptionParser
import docutils.nodes

__all__ = ["Html"]


class Html(BaseOutput):
    """ dmr output format class to write HTML output using the
    :mod:`docutils HTML translator <docutils.writers.html4css1>`."""
    name = "HTML"

    def output(self):
        writer = Writer()
        output = StringOutput(encoding="utf8")
        mydoc = copy.deepcopy(self.document.source)
        mydoc.reporter = self.document.source.reporter
        mydoc.settings = \
            OptionParser(components=(Writer,)).get_default_values()
        if config.footer:
            mydoc.append(docutils.nodes.footer(
                    config.footer,
                    docutils.nodes.Text(config.footer)))

        return writer.write(mydoc, output)
