""" dmr configuration parsing is done in several phases:

#. Command-line arguments are parsed to get the ``-c`` (config file)
   option.  All core options are parsed in order to give a good help
   message, but that's the only one we care about in this phase.
#. ``/etc/dmr.conf`` or the file specified with ``-c`` is parsed
#. ``$HOME/.dmr/config`` is parsed, and overwrites settings from
   ``/etc/dmr.conf``
#. :ref:`Core command-line arguments <configuration-global>` are
   re-parsed, and overwrite the settings in config files.
#. Once the output format is known, :ref:`options specific to the
   output format <configuration-output>` are parsed from the config
   files.
#. Output format options are parsed from the command line.
#. Options are parsed from the document that is being rendered.

Each phase overwrites values that were read in the previous phase.

Some options can take multiple values ``--exclude``.  These are
specified differently depending on where they are configured:

On the command line, give multiple option strings:

.. code-block:: bash

    dmr --exclude foo --exclude "bar and baz"

In the config file, use a quoted, space-separated list::

.. code-block:: cfg

    [global]
    exclude = foo "bar and baz"

In the document, give multiple option strings:

  .. options
     exclude foo
     exclude bar and baz

In-document options are specified as comments.  For instance:

.. code-block:: rst

  .. options
     footer
     exclude Experience

You can specify options for a specific output format thusly:

.. code-block:: rst

  .. options=json
     footer
     exclude Experience

Output-specific options override generic in-document options.

See :meth:`ConfigParser.RawConfigParser.getboolean` for acceptable
values for boolean configuration options.
"""

import os
import sys
import shlex
import argparse
import dmr.version
from dmr.logger import setup_logging, logger
import docutils.nodes
# pylint: disable=F0401
try:
    import configparser
except ImportError:
    import ConfigParser as configparser
# pylint: enable=F0401


__all__ = ["config", "parse", "options", "DMROption"]

_OPTIONS = []

#: A module-level :class:`argparse.Namespace` object that stores all
#: configuration for dmr.
config = argparse.Namespace(version=dmr.version.__version__,
                            name="dmr",
                            uri='http://github.com/stpierre/dmr')


class UnsetAction(argparse.Action):
    """ An argparse Action that unsets another item in the namespace. """

    def __init__(self, *args, **kwargs):
        self.target = None
        if 'target' in kwargs:
            self.target = kwargs.pop('target')
        kwargs['nargs'] = 0
        argparse.Action.__init__(self, *args, **kwargs)
        if not self.target and self.dest.startswith("no_"):
            self.target = self.dest[3:]
        else:
            self.target = self.dest

    def __call__(self, parser, namespace, values, option_string=None):
        if getattr(namespace, self.target):
            setattr(namespace, self.target, None)


def _get_footer():
    """ Get a footer that can optionally be appended to an output
    document.

    :returns: :class:`docutils.nodes.container`
    """
    return docutils.nodes.container(
            '', docutils.nodes.Text("Generated with "),
            docutils.nodes.reference('', config.name, refuri=config.uri))


class DMROption(object):
    """ Representation of an option that can be specified on the
    command line or in a config file. """

    def __init__(self, *args, **kwargs):
        """ See :meth:`argparse.ArgumentParser.add_argument` for a
        full list of accepted parameters.

        In addition to supporting all arguments and keyword arguments
        from :meth:`argparse.ArgumentParser.add_argument`, two
        additional keyword arguments are allowed.

        :param cf: A tuple giving the section and option name that
                   this argument can be referenced as in the config
                   file.
        :type cf: tuple
        :param inline: A string by which this argument can be
                       referenced in the inline options block of a
                       document.
        :type inline: string
        """
        self.args = args
        self.cf = None  # pylint: disable=C0103
        if 'cf' in kwargs:
            self.cf = kwargs.pop('cf')
        self.inline = None
        if 'inline' in kwargs:
            self.inline = kwargs.pop('inline')
        self.kwargs = kwargs
        self.action = None
        self.parser = None

    def add_to_parser(self, parser):
        """ Add this option to the given parser.

        :param parser: The parser to add the option to.
        :type parser: argparse.ArgumentParser
        :returns: argparse.Action
        """
        self.parser = parser
        self.action = parser.add_argument(*self.args, **self.kwargs)
        return self.action

    def from_config(self, cfp):
        """ Get the value of this option from the given
        :class:`ConfigParser.ConfigParser`.  If it is not found in the
        config file, the default is returned.  (If there is no
        default, None is returned.)

        :param cfp: The config parser to get the option value from
        :type cfp: ConfigParser.ConfigParser
        :returns: varies
        """
        try:
            for val in shlex.split(cfp.get(*self.cf)):
                self.parse_value(val)
        except (TypeError,  # self.cf is None
                configparser.NoSectionError, configparser.NoOptionError):
            pass

    def parse_value(self, value):
        """ Manually set or append the given value.

        :param value: The value to set, append, or otherwise
                      appropriately handle.
        """
        if self.action is None:
            # logging may not have been set up yet
            print("Options must be added to parsers before they can be parsed "
                  "from config")
            return
        return self.action(self.parser, config, value)


def options():
    """ Get a list of core options.  This is implemented as a function
    rather than as a module-level variable because it imports
    dmr.output, which itself imports dmr.config, so this list must be
    generated at run-time rather than at compile-time, or we get
    circular imports. """
    import dmr.output  # pylint: disable=W0621
    if not _OPTIONS:
        _OPTIONS.extend([
                DMROption("-c", "--config",
                          help="Specify a config file",
                          default="/etc/dmr.conf"),
                DMROption("--footer",
                          help="Include a dmr footer in the document",
                          default=False,
                          action='store_const',
                          const=_get_footer(),
                          cf=('global', 'footer'),
                          inline='footer'),
                DMROption("--no-footer",
                          help="Exclude the dmr footer from the document",
                          action=UnsetAction,
                          inline='no-footer'),
                DMROption(
                    "--exclude",
                    help="Exclude the named section from the final document",
                    action='append',
                    default=[],
                    cf=('global', 'exclude'),
                    inline='exclude'),
                DMROption(
                    "--include",
                    help="Include the named section in the final document",
                    action='append',
                    default=[],
                    cf=('global', 'include'),
                    inline='include'),
                DMROption("-v", "--verbose",
                          help="Be verbose",
                          action='count',
                          cf=('global', 'verbose')),
                DMROption("-f", "--format",
                          help="Output format",
                          default="html",
                          choices=[m.rsplit('.', 1)[-1]
                                   for m in dmr.output.__all__],
                          cf=('global', 'output_format')),
                DMROption("infile",
                          help="Input filename, or - to read from stdin",
                          default=sys.stdin,
                          nargs='?',
                          type=argparse.FileType('r'),
                          cf=('global', 'infile')),
                DMROption("-o", "--outfile",
                          help="Output filename, or - to write to stdout",
                          default=sys.stdout,
                          nargs='?',
                          type=argparse.FileType('w'),
                          cf=('global', 'outfile'))])
    return _OPTIONS


def _get_output_class(modname):
    """ Given the name of a module in :mod:`dmr.output`, get the
    output format class from that module.

    :param modname: The name of the module, *without* the leading
                    ``dmr.output.``.  E.g., ``html``, not
                    ``dmr.output.html``.
    :type modname: str
    :returns: type
    """
    classname = modname.title()
    return getattr(getattr(getattr(__import__("dmr.output.%s" % modname),
                                   "output"), modname), classname)


def _get_parser():
    """ Get an argument parser with all options (from
    :func:`dmr.config.options`) pre-loaded.

    :returns: :class:`argparse.ArgumentParser`
    """
    parser = argparse.ArgumentParser(
        description="Render a resume in different formats")
    for opt in options():
        opt.add_to_parser(parser)
    return parser


def _get_default_config(fmt, opts=None):
    """ Set a default config for the specified output format,
    overridden with the given options.  This should only be used by
    the test suite. """
    if opts is None:
        opts = dict()
    parser = _get_parser()
    for opt in options():
        opt.parse_value(None)
    config.format = fmt
    config.output_class = _get_output_class(fmt)
    for opt in config.output_class.get_options():
        opt.add_to_parser(parser)
        opt.parse_value(None)
    for opt, val in opts.items():
        setattr(config, opt, val)
    return config


def parse(argv=None):
    """ Parse command-line arguments and config file(s).

    :param argv: The argument list to parse, instead of
                 :attr:`sys.argv`
    :type argv: list
    :returns: :class:`argparse.Namespace`
    """
    if argv is None:
        argv = sys.argv
    # phase 1: get config file
    bootstrap = _get_parser().parse_known_args(namespace=config)[0]

    # phase 2: read config files
    cfp = configparser.SafeConfigParser()
    cfp.read([bootstrap.config, os.path.expanduser('~/.dmr/config')])
    for opt in options():
        opt.from_config(cfp)

    # phase 3: re-parse command line. verbose is a 'count' flag, so we
    # reset it so it doesn't just keep incrementing and incrementing.
    config.verbose = 0
    remaining = _get_parser().parse_known_args(namespace=config)[1]

    # phase 4: parse output format class options from config files
    parser = argparse.ArgumentParser()
    config.output_class = _get_output_class(config.format)
    for opt in config.output_class.get_options():
        opt.add_to_parser(parser)
        opt.from_config(cfp)

    # phase 5: parse output format class options from command line
    parser.parse_args(remaining, namespace=config)

    # phase 5 + 1: setup logging
    setup_logging(config.verbose)
    return config


def parse_document_options(opts):
    """ Parse local options from a document.

    :param opts: A list of option strings.  Each string should consist
                 of an option keyword and its value, separated by
                 whitespace.
    :type opts: list of strings
    """
    all_options = options() + config.output_class.get_options()
    for opt in opts:
        try:
            name, val = opt.split(None, 1)
        except ValueError:
            # just a flag
            name = opt
            val = True
        for opt in all_options:
            if name == opt.inline:
                opt.parse_value(val)
                break
        else:
            logger.error("Skipping unknown document option: %s" % opt)
