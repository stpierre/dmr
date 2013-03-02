""" This module provides a dmr output format to write LaTeX files
based on `Genshi <http://genshi.edgewall.org>`_ templates using
:mod:`dmr.output.genshi`.

See :ref:`configuration-genshi` for details on how the template is
selected. """

from dmr.output.genshi import GenshiOutput
from docutils.writers.latex2e import Writer

__all__ = ["Latex"]


class Latex(GenshiOutput):
    """ dmr output format to write LaTeX files using
    :class:`dmr.output.genshi.GenshiOutput`. """
    writer = Writer()
