""" Common place to hold the DMR version so we don't have to have it
in multiple files.  This file can be execfile()'d from anything that
needs the version when dmr is not installed, and imported from
anything that needs the version when it is installed. """

__version__ = "0.1.0"
