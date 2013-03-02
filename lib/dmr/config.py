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

Each phase overwrites values that were read in the previous phase.

See :meth:`ConfigParser.RawConfigParser.getboolean` for acceptable
values for boolean configuration options.
"""

import os
import sys
import argparse
import dmr.version
from dmr.logger import setup_logging
import docutils.nodes
# pylint: disable=F0401
try:
    import configparser
except ImportError:
    import ConfigParser as configparser
# pylint: enable=F0401


__all__ = ["config", "parse", "options", "DMROption"]

#: A module-level :class:`argparse.Namespace` object that stores all
#: configuration for dmr.
config = argparse.Namespace(version=dmr.version.__version__,
                            name="dmr",
                            uri='http://github.com/stpierre/dmr')


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
        from :meth:`argparse.ArgumentParser.add_argument`, one
        additional keyword argument is allowed.

        :param cf: A tuple giving the section and option name that
                   this argument can be referenced as in the config
                   file.
        :type cf: tuple
        """
        self.args = args
        self.cf = None  # pylint: disable=C0103
        if 'cf' in kwargs:
            self.cf = kwargs.pop('cf')
        self.kwargs = kwargs

        self.default = None
        self.action = 'store'
        self.const = None
        if 'default' in kwargs:
            self.default = kwargs['default']
        if 'action' in kwargs:
            self.action = kwargs['action']
        if 'const' in kwargs:
            self.const = kwargs['const']

        # Determine the name.  According to the official docs:
        #
        # "For optional argument actions, the value of dest is
        # normally inferred from the option strings. ArgumentParser
        # generates the value of dest by taking the first long option
        # string and stripping away the initial -- string. If no long
        # option strings were supplied, dest will be derived from the
        # first short option string by stripping the initial -
        # character. Any internal - characters will be converted to _
        # characters to make sure the string is a valid attribute
        # name."
        self.name = None
        if 'dest' in kwargs:
            self.name = kwargs['dest']
        elif not self.args[0].startswith("-"):
            self.name = self.args[0].replace("-", "_")
        else:
            # try to find a long flag
            for optstr in self.args:
                if optstr.startswith("--"):
                    self.name = optstr[2:].replace("-", "_")
                    break
            else:
                # no long flag, so use the first (short) option
                self.name = optstr[1:].replace("-", "_")

    def add_to_parser(self, parser):
        """ Add this option to the given parser.

        :param parser: The parser to add the option to.
        :type parser: argparse.ArgumentParser
        :returns: argparse.Action
        """
        return parser.add_argument(*self.args, **self.kwargs)

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
            if self.action == "store_const":
                if cfp.getboolean(*self.cf):
                    return self.const
                else:
                    return None
            else:
                return cfp.get(*self.cf)
        except (TypeError,  # self.cf is None
                configparser.NoSectionError, configparser.NoOptionError):
            return self.default  # None if no default


def options():
    """ Get a list of core options.  This is implemented as a function
    rather than as a module-level variable because it imports
    dmr.output, which itself imports dmr.config, so this list must be
    generated at run-time rather than at compile-time, or we get
    circular imports. """
    import dmr.output  # pylint: disable=W0621
    return [
        DMROption("-c", "--config",
                  help="Specify a config file",
                  default="/etc/dmr.conf"),
        DMROption("--footer",
                  help="Include a footer in the document with the DMR version",
                  default=False,
                  action='store_const',
                  const=_get_footer(),
                  cf=('global', 'footer')),
        DMROption("-v", "--verbose",
                  help="Be verbose",
                  action='count',
                  cf=('global', 'verbose')),
        DMROption("-f", "--format",
                  help="Output format",
                  default="html",
                  choices=[m.rsplit('.', 1)[-1] for m in dmr.output.__all__],
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
                  cf=('global', 'outfile'))]


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
   overridden with the given options.  This should only be used by the
   test suite. """
    if opts is None:
        opts = dict()
    for opt in options():
        setattr(config, opt.name, opt.default)
    config.format = fmt
    config.output_class = _get_output_class(fmt)
    for opt in config.output_class.get_options():
        setattr(config, opt.name, opt.default)
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
        setattr(config, opt.name, opt.from_config(cfp))

    # phase 3: re-parse command line
    remaining = _get_parser().parse_known_args(namespace=config)[1]

    # phase 4: parse output format class options from config files
    parser = argparse.ArgumentParser()
    config.output_class = _get_output_class(config.format)
    for opt in config.output_class.get_options():
        setattr(config, opt.name, opt.from_config(cfp))
        opt.add_to_parser(parser)

    # phase 5: parse output format class options from command line
    parser.parse_args(remaining, namespace=config)

    # phase 5 + 1: setup logging
    setup_logging(config.verbose)
    return config
