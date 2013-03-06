""" Input parsing routines for dmr. """

import sys
from dmr.config import config, parse_document_options
from dmr.data import Document, child_by_class
from dmr.logger import logger, fatal
import docutils.nodes
from docutils.utils import new_document
from docutils.frontend import OptionParser
from docutils.parsers.rst import Parser

__all__ = ['parse']


def parse(filehandle):
    """ Parse a document read from the given filehandle into a
    :class:`dmr.data.Document` object.

    The document must contain:

    * A top-level title, the resume owner's name;
    * A :class:`docutils.nodes.line_block` containing contact
      information for the resume, to be parsed with
      :func:`dmr.data.Contact.parse`; and
    * Any number of subsections that conform to the restrictions of
      the various :class:`dmr.data.Section` subclasses.

    :param filehandle: The file-like object to parse the document from.
    :type filehandle: file
    :returns: :class:`dmr.data.Document`
    """
    parser = Parser()
    settings = OptionParser(components=(Parser,)).get_default_values()
    logger.info("Parsing document from %s" % filehandle.name)
    document = new_document(filehandle.name, settings)
    try:
        parser.parse(filehandle.read(), document)
    except IOError:
        fatal("Could not parse %s: %s" % (filehandle.name, sys.exc_info()[1]))

    top = None
    options = dict()
    for child in document.children:
        if isinstance(child, docutils.nodes.Structural):
            if top:
                fatal("Document must have exactly one top-level heading")
            top = child
        elif isinstance(child, docutils.nodes.comment):
            contents = child_by_class(child, docutils.nodes.Text)
            if contents and contents.startswith("options"):
                opts = contents.splitlines()
                try:
                    # see if this is a format-specific option block
                    ofmt = opts[0].split("=")[1]
                    logger.debug("Found document options for %s: %s" %
                                 (ofmt, opts[1:]))
                except IndexError:
                    ofmt = None
                    logger.debug("Found default document options: %s" %
                                 opts[1:])
                options[ofmt] = opts[1:]
        else:
            logger.info("Skipping unknown node %s" % child)

    for ofmt in [None, config.format]:
        if ofmt in options:
            parse_document_options(options[ofmt])

    doc = Document.parse(top)
    doc.source = document
    return doc
