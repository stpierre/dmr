""" Input parsing routines for dmr. """

import sys
import dmr.data
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

    if len(document.children) != 1:
        fatal("Document must have exactly one top-level heading")

    doc = dmr.data.Document(source=document)

    top = document.children[0]
    doc.contact = dmr.data.Contact.parse(top)

    for data in top.children:
        if not isinstance(data, docutils.nodes.Structural):
            if not isinstance(data, (docutils.nodes.line_block,
                                     docutils.nodes.Titular)):
                logger.info("Skipping unknown node %s" % data)
            continue

        for sectiontype in dmr.data.sections:
            if sectiontype.is_valid(data):
                doc.append(sectiontype.parse(data))
                break
        else:
            logger.info("Skipping unknown section %s" %
                        dmr.data.get_title(data))
    return doc
