""" This module provides a JSON output format for dmr.  This is useful
if you want to get the data from a resume for use in other scripts or
programs.

.. note::

    **N.B.!** This output format is lossy!  Text formatting (e.g.,
    emphasis, etc.) is discarded, and only the actual text data is
    output.
"""

from __future__ import absolute_import
import json
from dmr.config import config, DMROption
from dmr.output.base import BaseOutput
from dmr.render import WhitespaceRemovingRenderer, ReferenceTransformer

__all__ = ["Json"]


class Json(BaseOutput):
    """ dmr output format class to write JSON output.  Note that this
    output format is lossy; text formatting (e.g., emphasis, etc.) is
    discarded. """

    def __init__(self, document):
        BaseOutput.__init__(self, document)
        self.renderer = WhitespaceRemovingRenderer(document.source,
                                                   ReferenceTransformer)

    @classmethod
    def get_options(cls):
        rv = BaseOutput.get_options()
        rv.append(DMROption("--pretty",
                            help="Output prettified JSON",
                            default=False,
                            action="store_true",
                            cf=('json', 'pretty')))
        return rv

    def output(self):
        jdata = dict()
        jdata.update(self.dump_contact(self.document.contact))
        for section in self.document:
            jdata[section.name.astext()] = \
                getattr(self,
                        "dump_%s" % section.type)(section)
        if config.footer:
            jdata['_comment'] = self.renderer(config.footer)
        if config.pretty:
            indent = 2
        else:
            indent = None
        return json.dumps(jdata, indent=indent)

    def dump_namedtuple(self, tpl):
        """ Dump a rendered namedtuple data class
        (:class:`dmr.data.Contact` and :class:`dmr.data.Dates`) to a
        dict in preparation for JSON serialization. """
        data = tpl.render(self.renderer)
        return dict([(field, getattr(data, field))
                     for field in tpl._fields])  # pylint: disable=W0212

    def dump_job(self, job):
        """ Dump a rendered :class:`dmr.data.Job` to a dict in preparation
        for JSON serialization. """
        data = job.render(self.renderer)
        return dict(employer=data.employer,
                    position=data.position,
                    dates=self.dump_dates(data.dates),
                    description=data.description)

    def dump_section(self, section):
        """ Dump a rendered :class:`dmr.data.Section` subclass object to a
        list in preparation for JSON serialization."""
        return section.render(self.renderer)[:]

    def dump_experience(self, section):
        """ Dump a rendered :class:`dmr.data.Exception` object to a list
        in preparation for JSON serialization."""
        return [self.dump_job(j) for j in section]

    dump_contact = dump_namedtuple
    dump_dates = dump_namedtuple
    dump_text = dump_section
    dump_list = dump_section
    dump_references = dump_section
