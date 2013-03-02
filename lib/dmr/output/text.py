""" This module provides a dmr output format to write plain text files
based on `Genshi`_ templates using :mod:`dmr.output.genshi`.

Although the `reST`_ input files are already plain text, this lets the
user provide a friendlier template for output if they so desire.

See :ref:`configuration-genshi` for details on how the template is
selected. """

from dmr.render import WhitespaceRemovingRenderer, ReferenceTransformer
from dmr.output.genshi import GenshiOutput

__all__ = ["Text"]


class Text(GenshiOutput):
    """ dmr output format to write plain text files using
    :class:`dmr.output.genshi.GenshiOutput`. """

    @property
    def renderer(self):
        if self._renderer is None:
            self._renderer = WhitespaceRemovingRenderer(self.document.source,
                                                        ReferenceTransformer)
        return self._renderer
