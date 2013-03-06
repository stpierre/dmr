""" The dmr data model. """
# -*- coding: utf-8 -*-

import re
import abc
from dmr.config import config
from dmr.logger import logger
import docutils.nodes
from collections import namedtuple, MutableSequence


def child_by_class(parent, nodecls):
    """ Get the first child of ``parent`` that is a member of
    ``nodecls``.  This differs from
    :func:`docutils.node.Node.first_child_matching_class`, which only
    returns the index of the first child.  This returns the actual
    child.

    :param parent: The parent node to search for children in.
    :type parent: docutils.node.Node
    :param nodecls: The :class:`docutils.node.Node` subclass to find
                    instances of (or children which are instances of a
                    subclass).  This can also be an instance of a Node
                    subclass.
    :type nodecls: type or docutils.node.Node
    :returns: docutils.node.Node instance or None
    """
    idx = parent.first_child_matching_class(nodecls)
    if idx is None:
        return None
    return parent.children[idx]


def _contain(parent):
    """ Given a parent element, add all of its children to a container
    element and return the container.  This lets us extract lines from
    line blocks and other such specific container elements and re-wrap
    them without any decoration (i.e., as just a bare line).

    :param node: The node to get children from.
    :type node: docutils.nodes.Node
    :returns: docutils.nodes.container
    """
    if len(parent.children) > 1:
        return docutils.nodes.container('', *parent.children)
    else:
        return parent.children[0]


def exclude(node):
    """ Return True if the node should be skipped.

    :param node: The node to check
    :type node: docutils.nodes.Node
    :returns: bool """
    names = [get_title(node)]
    for child in node.children:
        if isinstance(child, docutils.nodes.comment):
            contents = child_by_class(child, docutils.nodes.Text)
            if contents.startswith("group "):
                names.append(contents.split(None, 1)[-1])
    # if title or group name is explicitly included, override all excludes
    return (not any(n in config.include for n in names) and
            any(n in config.exclude for n in names))


def get_title(node):
    """ Given a :class:`docutils.nodes.Structural` node, get the
    content of the title of the section.

    :param node: The structural node to get the title from.
    :type node: docutils.nodes.Structural
    :returns: docutils.nodes.container
    """
    return _contain(child_by_class(node, docutils.nodes.Titular))


class Renderable(object):
    """ An abstract base class that provides a ``render`` method,
    which returns a new object of the given type with all internal
    data replaced by simple strings (as opposed to doctrees).
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def render(self, func):
        """ Render the data in this object using the given function
        to convert all data to strings.

        :param func: The function to apply to all doctrees in this dmr
                     data object.  It should take a single argument, a
                     :class:`doctress.node.Node` subclass, and should
                     return a string.
        """
        raise NotImplementedError


class Parseable(object):
    """ An abstract base class that provides a ``parse`` class method,
    which parses the given doctree and returns a new object of the
    given type from the data in it.
    """
    __metaclass__ = abc.ABCMeta

    @classmethod
    @abc.abstractmethod
    def parse(cls, node):
        """ Parse an object of this type out of the given node.

        :param node: The doctree to parse
        :type node: docutils.nodes.Node
        :returns: An object of this type
        """
        raise NotImplementedError


class RenderableNamedTuple(Renderable):
    """ An abstract base class to provide a working ``render`` method
    (as per :func:`dmr.data.Renderable.render` for namedtuple
    subclasses."""
    __metaclass__ = abc.ABCMeta

    def render(self, func):
        args = []
        for field in self._fields:  # pylint: disable=E1101
            val = getattr(self, field)
            if isinstance(val, list):
                args.append([func(v) for v in val])
            else:
                try:
                    args.append(func(val))
                except:  # pylint: disable=W0702
                    args.append(val)
        return self.__class__(*args)


# pylint: disable=C0103
ContactBase = namedtuple("ContactBase",
                         ["name", "address", "phone", "email", "URL", "other"])
DateBase = namedtuple("DateBase", ["start", "end"])
# pylint: enable=C0103


class Contact(ContactBase, RenderableNamedTuple, Parseable):
    """ An address block is a `line block
    <http://docutils.sourceforge.net/docs/user/rst/quickref.html#line-blocks>`_
    giving the contact information for a resume, an employer, a
    reference, or similar.  It consists of six different types of
    lines:

    * The **name** is freeform and must come on the first line, if it
      is needed at all.  See below for when a name is required and
      when it's not.
    * Any number of **phone numbers** may be provided; they must come
      after the name, but there is no other ordering requirement.  A
      phone number is any line that consists of dashes, parentheses,
      plus signs, whitespace, and digits, preceeded by an optional
      identifier.  E.g., ``(555) 555-5555``, ``cell: (02) 1234 5678``,
      and ``+44 01 56 60 56 60`` are all valid phone numbers.
      Additionally, any line containing a docutils reference that uses
      the ``tel:`` protocol will be considered a phone number.
    * Any number of **email addresses**, which also must come after
      the name.  Any line containing something that is automatically
      recognized by docutils as a reference *and* whose URI starts
      with ``mailto:`` is considered an email address.  (Note that
      it's usually unnecessary to specify ``mailto:`` explicitly;
      docutils is pretty smart about finding email addresses.  If
      you're still using that old bangpath address, though, you might
      need to.)
    * Any number of **URLs**, which also must come after the name.
      Any line containing something thing that is automatically
      recognized by docutils as a reference *and* which uses neither
      the ``mailto:`` nor the ``tel:`` protocol will be considered a
      URL.
    * The first contiguous set of lines that are not any of the above
      types will be considered the **physical address**.
    * All lines that are not any of the above types wil be considered
      **other data**.  Other data must come after the physical
      address, and the physical address must be separated from the
      other data by a phone number, URL, or email address.  See the
      examples below.

    If the address block describes a reference, then the first line
    must be that person's name.  Otherwise, the name will be taken
    from the title of the section the address block is in, and must
    *not* be included in the address block itself.  (See below for
    examples to clarify this.)

    Outside of the few ordering requirements listed, order is neither
    required nor respected; the order of address elements in the
    output document is specified by the output format class.  The
    canonical output order is: name, address, phone, email, url,
    other.  No output format is required to honor that.

    .. rubric:: Examples

    So the start of a resume might look like:

    .. code-block:: rst

        ============================
         Dennis MacAlistair Ritchie
        ============================

        | 1234 No. Such Ln.
        | Berkeley Heights, NJ 07922
        | (908) 555-5555
        | dmr@lucent.com

    Whereas a personal reference might look like:

    .. code-block:: rst

        References
        ==========

        | Dennis MacAlistair Ritchie
        | 1234 No. Such Ln.
        | Berkeley Heights, NJ 07922
        | (908) 555-5555
        | dmr@lucent.com

    Note the different ways the name is specified.

    Physical address matching is greedy, so if you have several
    unrecognizable lines in a row, they will all become the physical
    address.  Consider this example:

    .. code-block:: rst

        ============================
         Dennis MacAlistair Ritchie
        ============================

        | 1234 No. Such Ln.
        | Berkeley Heights, NJ 07922
        | "I invented C."
        | (908) 555-5555
        | dmr@lucent.com

    In this case, the physical address would have *three* lines --
    "1234 No. Such Ln.", 'Berkeley Heights, NJ 07922", and "'I
    invented C.'"  In order to treat the final line as "other data"
    instead of as the physical address, it must be separated from the
    physical address by another data type.  E.g.:

    .. code-block:: rst

        ============================
         Dennis MacAlistair Ritchie
        ============================

        | 1234 No. Such Ln.
        | Berkeley Heights, NJ 07922
        | (908) 555-5555
        | dmr@lucent.com
        | "I invented C."
    """
    phone_re = re.compile(r'(?:.*:\s*)?[-\s.()+0-9]+$')

    @classmethod
    def parse(cls, node):
        """ Parse a node into a :class:`dmr.data.Contact` object.  The
        node must either a) be a :class:`docutils.nodes.line_block`;
        or b) contain a :class:`docutils.nodes.Titular` and a
        :class:`docutils.nodes.line_block`.

        :param block: The line block to parse.
        :type block: docutils.nodes.Node
        :returns: :class:`dmr.data.Contact`
        """
        if isinstance(node, docutils.nodes.line_block):
            block = node
            name = None
        else:
            name = get_title(node)
            logger.debug("Parsing address block for %s" % name)
            block = child_by_class(node, docutils.nodes.line_block)
            if block is None:
                return cls(name, [], [], [], [], [])

        in_address = True
        address = []
        phone = []
        email = []
        url = []
        other = []
        for rawline in block.children:
            if isinstance(rawline, docutils.nodes.comment):
                continue
            line = _contain(rawline)
            ref = child_by_class(rawline, docutils.nodes.reference)
            if not name:
                name = line
                logger.debug("Parsing address block for %s" % name)
            elif ref:
                # email address, phone number, or url
                if ref.attributes['refuri'].startswith("mailto:"):
                    email.append(line)
                elif ref.attributes['refuri'].startswith("tel:"):
                    phone.append(line)
                else:
                    url.append(line)
                if in_address and address:
                    in_address = False
            elif cls.phone_re.match(line.astext()):
                phone.append(line)
                if in_address and address:
                    in_address = False
            elif in_address:
                address.append(line)
            else:
                other.append(line)
        return cls(name, address, phone, email, url, other)


class Dates(DateBase, RenderableNamedTuple, Parseable):
    """ A date range is a one-line paragraph giving a range of dates.
    The dates themselves are not parsed; only the start and end of the
    range are determined.  The start and end may be separated:

    * By the word 'to' surrounded by whitespace;
    * By a hyphen surrounded by whitespace;
    * By a hyphen with optional whitespace around it, if neither date
      contains a hyphen.

    In other words, the following are all valid::

        1 February 2013 to 27 February 2013
        2-1-2013 to 2-27-2013
        2013-1-2 - 2013-27-2
        1 Feb 2013-27 Feb 2013
        1999-2004
        Marceau, Nonidi 9 Ventôse an 221 - Présent

    The following are invalid::

        2013-1-2-2013-27-2
        1 février 2013 à 27 février 2013

    The latter invalid example is a localization problem, which
    someone should probably solve some day.  However, it should be
    noted that the actual display of the separator between the dates
    is left to the output format; the separator used in the source
    file is not preserved.  (I.e., non-English-language resumes can
    use the hyphen as a separator, and the appropriate word or
    separator in the output formatter.)
    """
    regexes = [re.compile(r'\s+(?:-|to)\s+'),
               re.compile(r'\s*-\s*')]

    @classmethod
    def parse(cls, node):
        # we first try splitting on a space-delimited dash or 'to',
        # since dates can themselves contain dashes.  if that fails,
        # we split on a non-space delimited dash, which could be
        # ambiguous.
        for regex in cls.regexes:
            try:
                return cls(*regex.split(node.astext(), maxsplit=1))
            except TypeError:
                pass
        logger.info("No valid date range could be determined from %s" %
                    node.astext())
        return cls(node.astext(), None)

    def render(self, func):
        # a Dates object already stores strings, not doctrees, so just
        # return this object.  This should be fixed some day, but
        # splitting doctrees is hard.
        return self


class Job(MutableSequence, Renderable, Parseable):  # pylint: disable=R0901
    """ Representation of an element in a :ref:`input-experience`
    section.  We call it a "Job," but it could be schooling or
    anything else with dates and a bullet list description.  It
    contains:

    * An :ref:`input-address-block` (optional), giving the employer's
      contact information; and
    * A :ref:`input-dates` (optional), giving the dates in the
      position; and
    * A bulleted list of your duties at that employer.
    """

    def __init__(self, employer=None, position=None, dates=None, start=None,
                 end="Present", description=None):
        """
        :param employer: The employer (or school, etc.)
        :type employer: dmr.data.Contact
        :param position: The position at said employer.  This is
                         completely optional, for instance for
                         education history.
        :type position: str
        :param dates: The date range for the given job.  Either
                      provide ``dates`` or ``start`` and ``end``, but
                      not both.
        :type dates: dmr.data.Dates
        :param start: The start of the date range for the given job.
                      Either provide ``dates`` or ``start`` and
                      ``end``, but not both.
        :type start: str
        :param end: The end of the date range for the given job.
                    Either provide ``dates`` or ``start`` and ``end``,
                    but not both.
        :type end: str
        :param description: The itemized description of the position.
        :type description: list of strings
        """
        Renderable.__init__(self)
        Parseable.__init__(self)

        #: The employer (or school, etc.) as a
        #: :class:`dmr.data.Contact`
        self.employer = employer

        #: The position at the employer, or None if not applicable.
        self.position = position

        if dates is not None:
            #: The dates at this job, as a :class:`dmr.data.Dates`
            self.dates = dates
        else:
            self.dates = Dates(start, end)

        if description is None:
            #: A list of things you did at the job.
            self.description = []
        else:
            self.description = description

    @classmethod
    def parse(cls, node, employer=None):  # pylint: disable=W0221
        """
        :param node: The node to parse a job from
        :type node: docutils.nodes.Node
        :param employer: Optionally, the employer for this job, if it was
                         provided elsewhere and the job node only
                         describes a position at the employer.
        :type employer: dmr.data.Contact
        :returns: :class:`dmr.data.Job`
        """
        if employer is None:
            employer = Contact.parse(node)
            position = None
            logger.debug("Parsing job at %s" % employer.name)
        else:
            position = get_title(node)
            logger.debug("Parsing job %s at %s" % (position, employer))

        dates = Dates(None, None)
        datenode = child_by_class(node, docutils.nodes.paragraph)
        if datenode:
            dates = Dates.parse(datenode)

        job = cls(position=position, employer=employer, dates=dates)
        for item in child_by_class(node, docutils.nodes.bullet_list).children:
            if isinstance(item, docutils.nodes.comment):
                continue
            job.append(child_by_class(item, docutils.nodes.paragraph))
        return job

    def render(self, func):
        rv = self.__class__(employer=self.employer.render(func),
                            position=None,
                            dates=self.dates.render(func),
                            description=[func(l) for l in self.description])
        if self.position:
            rv.position = func(self.position)
        return rv

    def _get_start(self):
        """ The start date of the position """
        return self.dates.start

    def _set_start(self, val):
        """ Setter for self.dates.start """
        self.dates = Dates(val, self.dates.end)

    start = property(_get_start, _set_start)

    def _get_end(self):
        """ The end date of the position """
        return self.dates.end

    def _set_end(self, val):
        """ Setter for self.dates.end """
        self.dates = Dates(self.dates.start, val)

    end = property(_get_end, _set_end)

    def __getitem__(self, idx):
        return self.description[idx]

    def __setitem__(self, idx, value):
        self.description[idx] = value

    def __delitem__(self, idx):
        del self.description[idx]

    def insert(self, idx, value):
        self.description.insert(idx, value)

    def __len__(self):
        return len(self.description)

    def __iter__(self):
        return iter(self.description)

    def __contains__(self, other):
        return other in self.description

    def __repr__(self):
        desc_str = self.description[0:2]
        if len(self.description) > 2:
            desc_str.append("...")
        return "%s(employer=%s, position=%s, dates=%s, description=%s)" % (
            self.__class__.__name__, self.employer, self.position, self.dates,
            desc_str)


class SectionType(object):
    """ This very simple descriptor class exists only to get the name
    of the owner class.  This way, every section can have a ``type``
    attribute that is in the ``__class__.__name__`` attribute
    (lowercased), which can be used by output formats to determine the
    type of a section without needing to use ``__class__`` magic."""

    def __get__(self, inst, owner):
        return owner.__name__.lower()


class Section(list, Renderable, Parseable):
    """ Abstract representation of a resume section """
    allowed_child_node_types = [docutils.nodes.comment]
    required_child_node_types = []
    type = SectionType()

    def __init__(self, name):
        """
        :param name: The name (title) of the section
        :type name: docutils.nodes.Text
        """
        #: The name (title) of the section, as
        #: :class:`docutils.nodes.Text`
        Renderable.__init__(self)
        Parseable.__init__(self)
        self.name = name
        list.__init__(self, [])

    def render(self, func):
        rv = self.__class__(func(self.name))
        rv.extend([func(p) for p in self])
        return rv

    @classmethod
    def parse(cls, node):
        """ Parse an object of this type out of the given node.

        :param node: The doctree to parse
        :type node: docutils.nodes.Node
        :returns: An object of this type
        """
        return cls(get_title(node))

    @classmethod
    def is_valid(cls, node):
        """ Return True if the node contains a valid section of this
        type, False otherwise.  Subclasses must not return false
        positives in any case, since :func:`dmr.input.parse` does not
        necessarily check sections in any particular order.

        :param node: The node to check
        :type node: docutils.nodes.Node
        :returns: bool """
        return (all(any(isinstance(el, nodecls)
                       for nodecls in cls.allowed_child_node_types)
                   for el in node.children[1:]) and
                all(node.first_child_matching_class(nodecls) is not None
                    for nodecls in cls.required_child_node_types))

    def __repr__(self):
        return "%s: %s%s" % (self.__class__.__name__, self.name,
                             list.__repr__(self))


class Text(Section):
    """ A Text section contains *only* freeform text -- an objective,
    for instance.  This is the simplest section.

    A section header with no content (e.g., "References Available Upon
    Request") will be treated as a Text section.

    .. rubric:: Examples

    .. code-block:: rst

        Objective
        =========

        To obtain a rewarding, high-level position inventing C.

    .. code-block:: rst

        References Available Upon Request
        =================================
    """
    allowed_child_node_types = Section.allowed_child_node_types + \
        [docutils.nodes.paragraph]

    @classmethod
    def parse(cls, node):
        section = super(Text, cls).parse(node)
        section.extend(c for c in node.children[1:]
                       if not isinstance(c, docutils.nodes.comment))
        return section


class Experience(Section):
    """
    The Experience section is by far the most complex section.  It is
    useful for job experience, education history, and anything that
    consists of multiple discrete items with dates and descriptions.
    It may take one of two formats:

    .. _experience-with-positions:

    .. rubric:: With Positions

    For most job experience sections, you'll want to use the format
    that allows you to specify both employers and positions.  In this
    case, the Experience section must consist only of any number of
    subsections, each of which describes an employer.  Each employer
    section must itself contain:

    * An :ref:`input-address-block` (optional), giving the employer's
      contact information; and
    * Any number of subsections, each of which describes a position
      held at that employer.

    .. note::

        This makes it simple and efficient to specify multiple jobs
        you held at a single employer.

    Each position subsection is a :ref:`input-job`.

    See the examples below.

    .. _experience-without-positions:

    .. rubric:: Without Positions

    In this format, you only specify employers, not positions.  This
    is useful for education sections, where you often wish to list the
    school, but a "position" as such is nonsensical.  (Of course, more
    complex education sections will likely wish to use the
    :ref:`format with positions <experience-with-positions>` in order
    to present more data.)

    The positionless format is simply the :ref:`format with positions
    <experience-with-positions>` with one level of subsection removed.
    The Experience section must consist only of any number of
    subsections, each of which is a :ref:`input-job`.

    See the examples below.

    .. rubric:: Examples

    This is an example of an :ref:`Experience section with positions
    <experience-with-positions>`:

    .. code-block:: rst

        Experience
        ==========

        Bell Labs
        ---------
        | 600 Mountain Ave.
        | New Providence, NJ 07974

        Scientist
        ~~~~~~~~~
        1967 - 1975

        * Invented C.
        * Invented C while inventing UNIX.
        * Wrote *The C Programming Language*.

        Research Fellow
        ~~~~~~~~~~~~~~~
        1975 - 1996

        * Developed ANSI C (C89).
        * Won the Turing Award and the Hamming Medal.

        Lucent Technologies
        -------------------

        Chair, System Software Research Department
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        1996 - 2007

        * Got about a zillion more awards for being the guy who
          invented C.

    This is an example of an :ref:`Experience section without
    positions <experience-without-positions>`:

    .. code-block:: rst

        Education
        =========

        Harvard University
        ------------------
        1959 - 1963

        * B.S., Physics
        * B.A., Applied Mathematics

        Harvard University
        ------------------
        1963 - 1967

        * PhD, Applied Mathematics
        * Dissertation: "Program Structure and Computational
          Complexity"
    """
    allowed_child_node_types = Section.allowed_child_node_types + \
        [docutils.nodes.Structural, docutils.nodes.Titular,
         docutils.nodes.line_block]
    required_child_node_types = [docutils.nodes.Structural]

    def render(self, func):
        rv = self.__class__(func(self.name))
        rv.extend([job.render(func) for job in self])
        return rv

    @classmethod
    def parse(cls, node):
        section = super(Experience, cls).parse(node)
        logger.debug("Parsing %s node %s" % (cls.type, section.name))
        for employernode in node.children:
            if not isinstance(employernode, docutils.nodes.Structural):
                continue

            if exclude(employernode):
                logger.debug("Skipping excluded employer %s" %
                             get_title(employernode))
                continue

            # Two ways this could be structured:
            # * With just employer (e.g., an Education section, which
            #   might only list the schools attended, not "position")
            # * Nested sections for employer and position
            if employernode.first_child_matching_class(
                docutils.nodes.Structural) is not None:
                # nested sections
                address = Contact.parse(employernode)
                for jobnode in employernode.children:
                    if not isinstance(jobnode, docutils.nodes.Structural):
                        if not isinstance(jobnode, (docutils.nodes.line_block,
                                                    docutils.nodes.Titular,
                                                    docutils.nodes.comment)):
                            logger.info("Skipping unknown node %s in job node"
                                        % jobnode)
                        continue
                    if exclude(jobnode):
                        logger.debug("Skipping excluded job %s" %
                                     get_title(jobnode))
                        continue

                    job = Job.parse(jobnode, employer=address)
                    section.append(job)
            else:
                section.append(Job.parse(employernode))
        return section


class List(Section):
    """ A List section contains *only* a bulleted list -- for example,
    a list of publications, or related experience.

    .. rubric:: Examples

    .. code-block:: rst

        Other Qualifications
        ====================

        * Invented C.
        * No seriously.
        * Invented a lot of UNIX, too.
     """
    allowed_child_node_types = Section.allowed_child_node_types + \
        [docutils.nodes.bullet_list]
    required_child_node_types = [docutils.nodes.bullet_list]

    @classmethod
    def parse(cls, node):
        section = super(List, cls).parse(node)
        for item in child_by_class(node, docutils.nodes.bullet_list).children:
            section.append(child_by_class(item, docutils.nodes.paragraph))
        return section


class References(Section):
    """ A References section contains *only* a series of :ref:`Address
    Blocks <input-address-block>`.

    .. rubric:: Examples

    .. code-block:: rst

        References
        ==========

        | Dennis MacAlistair Ritchie
        | 1234 No. Such Ln.
        | Berkeley Heights, NJ 07922
        | (908) 555-5555
        | dmr@lucent.com
    """
    allowed_child_node_types = Section.allowed_child_node_types + \
        [docutils.nodes.line_block]
    required_child_node_types = [docutils.nodes.line_block]

    def render(self, func):
        rv = self.__class__(func(self.name))
        rv.extend([contact.render(func) for contact in self])
        return rv

    @classmethod
    def parse(cls, node):
        section = super(References, cls).parse(node)
        for item in node.children[1:]:
            if not isinstance(item, (docutils.nodes.line_block,
                                     docutils.nodes.comment)):
                logger.info("Skipping unknown node in %s section '%s': %s" %
                            (cls.type, section.name.astext(), item))
                continue
            section.append(Contact.parse(item))
        return section


class Document(list, Parseable):
    """ Every dmr resume must start with a top-level title that
    contains the full name of the person whose resume it is.  For
    example:

    .. code-block:: rst

        ============================
         Dennis MacAlistair Ritchie
        ============================

    Immediately after the title there should be an
    :ref:`input-address-block` for the person whose resume it is,
    followed by any number of other :ref:`input-sections`.

    That's it -- a top title, an address block, and then other
    sections.  All of the data is held in other sections."""

    def __init__(self, source=None, contact=None,
                 sections=None):  # pylint: disable=W0621
        """
        :param source: The :class:`docutils.nodes.document`
                       representing the original doctree.
        :type source: docutils.nodes.document
        :param contact: The contact for the resume (i.e., the person
                        whose resume it is).
        :type contact: dmr.data.Contact
        :param sections: A list of sections in the document.
        :type sections: list of :class:`dmr.data.Section` subclass
                        objects
        """
        if sections is None:
            list.__init__(self, [])
        else:
            list.__init__(self, sections)
        Parseable.__init__(self)

        #: The contact for the resume (i.e., the person whose resume
        #: it is), as a :class:`dmr.data.Contact`.
        self.contact = contact

        #: The :class:`docutils.nodes.document` representing the
        #: original doctree.
        self.source = source

    @classmethod
    def parse(cls, node):
        doc = cls()
        doc.contact = Contact.parse(node)

        for data in node.children:
            if not isinstance(data, docutils.nodes.Structural):
                if not isinstance(data, (docutils.nodes.line_block,
                                         docutils.nodes.Titular,
                                         docutils.nodes.comment)):
                    logger.info("Skipping unknown node %s" % data)
                continue

            if exclude(data):
                logger.debug("Skipping excluded section %s" % get_title(data))
                continue

            for sectiontype in sections:
                if sectiontype.is_valid(data):
                    doc.append(sectiontype.parse(data))
                    break
            else:
                logger.info("Skipping unknown section %s" % get_title(data))
        return doc

    @property
    def sections(self):
        """ A list of names of the sections contained in this document """
        return [s.name.astext() for s in self]

    def __repr__(self):
        return "%s(%s): %s" % (self.__class__.__name__, self.contact,
                             self.sections)

    def index(self, val):
        try:
            return list.index(val)
        except ValueError:
            return self.sections.index(val)


sections = [c for c in globals().values()  # pylint: disable=C0103
            if Section in getattr(c, "__mro__", []) and c != Section]
