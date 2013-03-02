""" Logging for dmr. """

import sys
import logging
import logging.handlers

__all__ = ["logger", "fatal"]

#: :class:`logging.Logger` object that all dmr modules should use for
#:output.
logger = logging.getLogger(sys.argv[0])


def setup_logging(verbose=0):
    """ Set up logging according to the verbose level given on the
    command line.

    :param verbose: Verbose level.  0 through 3 are specifically
                    handled; higher means more verbose.
    :type verbose: int
    :returns: logging.RootLogger - :attr:`dmr.logger.logger`
    """
    stderr = logging.StreamHandler()
    level = logging.WARNING
    if verbose == 1:
        level = logging.INFO
    elif verbose > 1:
        level = logging.DEBUG
        if verbose > 2:
            stderr.setFormatter(logging.Formatter(
                    "%(asctime)s: %(levelname)s: %(message)s"))
        else:
            stderr.setFormatter(logging.Formatter(
                    "%(levelname)s: %(message)s"))
    logger.setLevel(level)
    logger.addHandler(stderr)
    syslog = logging.handlers.SysLogHandler("/dev/log")
    syslog.setFormatter(logging.Formatter("%(name)s: %(message)s"))
    logger.addHandler(syslog)
    logger.debug("Setting verbose to %s" % verbose)
    return logger


def fatal(msg, rv=1):
    """ Log a fatal message and raise :exc:`SystemExit`.

    :param msg: The message to log
    :type msg: str
    :param rv: The return value to exit with.
    :type rv: int
    :raises: SystemExit
    """
    logger.fatal(msg)
    raise SystemExit(rv)
