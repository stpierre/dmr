""" Utilities for rendering doctrees. """

import re
import copy
import docutils.nodes
from docutils.frontend import OptionParser


class Renderer(object):
    """ Get a renderer callable suitable for passing to
    :func:`dmr.data.Renderable.render`. """

    def __init__(self, document, visitor_cls):
        """
        :param document: The docutils document to use as a rendering
                         base.  This is *not* the document to render,
                         but rendering a snippet requires a full
                         document for things like settings and a
                         reporter.
        :type document: docutils.nodes.document
        :param visitor_cls: A :class:`docutils.nodes.NodeVisitor`
                            subclass to use to walk the doctrees that
                            are rendered.  A new visitor is
                            instantiated for each snippet that is
                            rendered, because we are not rendering
                            full documents and so a visitor does not
                            necessarily get reset between renderings.
        :type visitor_cls: docutils.nodes.NodeVisitor
        """
        self.visitor_cls = visitor_cls
        self.document = document

    def __call__(self, snippet):
        mydoc = copy.deepcopy(snippet)
        visitor = self.visitor_cls(self.document)
        mydoc.walkabout(visitor)
        return ''.join(visitor.body)


class WriterRenderer(Renderer):
    """ Get a renderer callable for the given docutils Writer,
    suitable for passing to
    :func:`dmr.data.Renderable.render`. """
    def __init__(self, document, writer):
        document.settings = \
            OptionParser(components=(writer.__class__,)).get_default_values()
        Renderer.__init__(self, document, writer.translator_class)
        self.writer = writer


class WhitespaceRemovingRenderer(Renderer):
    """ :class:`dmr.render.Renderer` that removes newlines and
    duplicate whitespace. """
    whitespace = re.compile(r'\s+')

    def __call__(self, snippet):
        return self.whitespace.sub(' ', Renderer.__call__(self, snippet))


class ReferenceTransformer(docutils.nodes.GenericNodeVisitor):
    """ Node visitor that transforms :class:`docutils.nodes.reference`
    nodes into plain-text representations of those references. """

    def __init__(self, document):
        docutils.nodes.GenericNodeVisitor.__init__(self, document)
        self.body = []
        self.skip = False

    def default_visit(self, node):
        if not self.skip and not node.children:
            self.body.append(node.astext())
        self.skip = False

    def visit_reference(self, node):
        """ Render a reference node """
        if (not node.attributes['refuri'].startswith("mailto:") and
            not node.attributes['refuri'].startswith("tel:") and
            node.astext() != node.attributes['refuri']):
            self.body.append("%s <%s>" % (node.astext(),
                                          node.attributes['refuri']))
            self.skip = True  # skip content of this node

    def default_departure(self, node):
        pass
