""" `Genshi`_ helper output format for dmr.  This helper output module
should not be called by itself, but can be used by other output
modules to easily add Genshi templating abilities. """

from __future__ import absolute_import
import os
from pkg_resources import resource_filename  # pylint: disable=E0611
import genshi.core
import genshi.template
from dmr.render import WriterRenderer
from dmr.logger import logger
from dmr.config import config, DMROption
from dmr.output.base import BaseOutput

__all__ = ["GenshiOutput"]

#: Do not expose the output class defined in this module as a usable
#: output format.
__expose__ = False


def removecomment(stream):
    """ A `Genshi`_ filter that removes comments from the stream.

    :param stream: The Genshi stream to remove comments from
    :type stream: genshi.core.Stream
    :returns: tuple of ``(kind, data, pos)``, as when iterating
              through a Genshi stream
    """
    for kind, data, pos in stream:
        if kind is genshi.core.COMMENT:
            continue
        yield kind, data, pos


class GenshiOutput(BaseOutput):
    """ dmr output class that renders the data in the document with a
    `Genshi`_ template.  This class is
    not a usable output format itself; child classes can inherit from
    it to implement their own Genshi templating.

    The child class will use a docutils Writer to translate all of the
    doctrees in the :class:`dmr.data.Document` that will be rendered.
    """

    #: A :class:`docutils.writers.Writer` subclass that will be used
    #: to translate the snippets in the dmr document.
    writer = None

    def __init__(self, document):
        BaseOutput.__init__(self, document)
        self._renderer = None

    @classmethod
    def get_options(cls):
        try:
            tmpl_path = resource_filename(config.name,
                                          "share/dmr/templates")
        except ImportError:
            tmpl_path = "templates"

        rv = BaseOutput.get_options()
        rv.append(DMROption("--template-path",
                            help="Path to Genshi templates",
                            default=tmpl_path,
                            type=os.path.abspath,
                            cf=('genshi', 'template_path')))
        rv.append(DMROption("--template",
                            help="Template to use, relative to template path",
                            default="%s.genshi" % cls.__name__.lower(),
                            cf=(cls.__name__.lower(), 'template')))
        return rv

    @property
    def renderer(self):
        """ Get a renderer for a doctree snippet.  By default, this
        uses :class:`dmr.data.WriterRenderer`, which passes the
        snippets through to a docutils Writer class. """
        if self._renderer is None:
            self._renderer = WriterRenderer(self.document.source,
                                            self.writer)
        return self._renderer

    def output(self):
        logger.debug("Rendering document")
        data = dict(document=self.document,
                    contact=self.document.contact.render(self.renderer),
                    sections=[],
                    footer=None)
        for section in self.document:
            logger.debug("Rendering section '%s'" % section.name)
            data['sections'].append(section.render(self.renderer))

        if config.footer:
            data['footer'] = self.renderer(config.footer)

        tmpl_paths = [config.template_path,
                      os.path.expanduser('~/.dmr/templates')]
        logger.debug("Loading templates from %s" % tmpl_paths)
        loader = genshi.template.TemplateLoader(tmpl_paths)
        logger.info("Loading template at %s" % config.template)
        tmpl = loader.load(config.template,
                           cls=genshi.template.NewTextTemplate)
        logger.debug("Generating template output stream")
        stream = tmpl.generate(**data).filter(removecomment)
        logger.debug("Rendering template")
        try:
            return stream.render('text', strip_whitespace=False)
        except TypeError:
            return stream.render('text')
