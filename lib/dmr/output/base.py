""" Base dmr output module. """

#: Do not expose the output class defined in this module as a usable
#: output format.
__expose__ = False


class ClassName(object):
    """ This very simple descriptor class exists only to get the name
    of the owner class.  This is used to set a sensible default
    display name for output plugins. """

    def __get__(self, inst, owner):
        return owner.__name__


class BaseOutput(object):
    """ Base dmr output class.  All dmr output format classes should
    inherit from this class. """
    name = ClassName()

    def __init__(self, document):
        """
        :param document: The DMR document to output
        :type document: dmr.data.Document
        """
        #: The :class:`dmr.data.Document` object to output
        self.document = document

    @classmethod
    def get_options(cls):
        """ Get a list of options to parse from the config files and
        command line when this output class is selected.

        :returns: list - A list of :class:`dmr.config.DMROption` objects
        """
        return []

    def output(self):
        """ Get the document output as rendered by this output format.
        Child classes must implement this method.

        :returns: str - The document output
        """
        raise NotImplementedError
