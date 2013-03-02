# -*- coding: utf-8 -*-

import copy
import dmr.data
from unittest import TestCase
from docutils.utils import new_document
from docutils.frontend import OptionParser
from docutils.parsers.rst import Parser
from dmr.render import WhitespaceRemovingRenderer, ReferenceTransformer


def get_renderer():
    settings = OptionParser(components=(Parser,)).get_default_values()
    document = new_document("/tmp/fake", settings)
    return WhitespaceRemovingRenderer(document, ReferenceTransformer)


renderer = get_renderer()


def parse(data):
    parser = Parser()
    settings = OptionParser(components=(Parser,)).get_default_values()
    document = new_document("/tmp/fake", settings)
    parser.parse(data, document)
    return document


def job2dict(job):
    """ convert a dmr.data.Job object to a dict so it can be compared
    for equality to other Job objects """
    return dict(employer=tuple(job.employer),
                position=job.position,
                dates=tuple(job.dates),
                description=job.description)


class TestContact(TestCase):
    minimal_expected = ("Testy O'Tester", [], [], [], [], [])
    full_expected = (
        "Testy O'Tester",
        ["1234 No. Such St.", "Nowhere, XX 12345"],
        ["cell: +1 (123) 456-7890", "(02) 1234 5678",
         "tel:(0123)12345678"],
        ["not-a-real-address@yahoo.com"],
        ["http://myurl.example.com", "http://github.com/stpierre/dmr"],
        ["Other data here", "Get some markup into the address"])

    def _test(self, data, expected):
        doc = parse(data)
        contact = dmr.data.Contact.parse(doc.children[0])
        self.assertEqual(tuple(contact.render(renderer)), expected)

    def test_minimal_line_block(self):
        """ Parse line-block Contact with minimal data """
        data = "| Testy O'Tester"
        self._test(data, self.minimal_expected)

    def test_minimal_header(self):
        """ Parse section header Contact with minimal data """
        data = """
Testy O'Tester
============== """
        self._test(data, self.minimal_expected)

    def test_full_line_block(self):
        """ Parse line-block Contact with all data """
        data = """
| Testy O'Tester
| 1234 No. Such St.
| Nowhere, XX 12345
| cell: +1 (123) 456-7890
| (02) 1234 5678
| `<tel:(0123)12345678>`_
| not-a-real-address@yahoo.com
| http://myurl.example.com
| http://github.com/stpierre/dmr
| Other data here
| Get some *markup* into the address
"""
        self._test(data, self.full_expected)

        data = """
| Testy O'Tester
| cell: +1 (123) 456-7890
| http://myurl.example.com
| 1234 No. Such St.
| Nowhere, XX 12345
| (02) 1234 5678
| Other data here
| not-a-real-address@yahoo.com
| Get some *markup* into the address
| http://github.com/stpierre/dmr
| `<tel:(0123)12345678>`_
"""
        self._test(data, self.full_expected)

    def test_full_header(self):
        """ Parse section header Contact with all data """
        data = """
Testy O'Tester
==============

| cell: +1 (123) 456-7890
| http://myurl.example.com
| 1234 No. Such St.
| Nowhere, XX 12345
| (02) 1234 5678
| Other data here
| not-a-real-address@yahoo.com
| Get some *markup* into the address
| `<tel:(0123)12345678>`_
| http://github.com/stpierre/dmr
"""
        self._test(data, self.full_expected)


class TestDates(TestCase):
    def test(self):
        """ Parse date ranges """
        cases = [("1 February 2013 to 27 February 2013",
                  ("1 February 2013", "27 February 2013")),
                 ("2-1-2013 to 2-27-2013", ("2-1-2013", "2-27-2013")),
                 ("2013-1-2 - 2013-27-2", ("2013-1-2", "2013-27-2")),
                 ("1 Feb 2013-27 Feb 2013", ("1 Feb 2013", "27 Feb 2013")),
                 ("1999-2004", ("1999", "2004")),
                 (u"Marceau, Nonidi 9 Ventôse an 221 - Présent",
                  (u"Marceau, Nonidi 9 Ventôse an 221", u"Présent")),
                 # invalid date ranges
                 ("2013-1-2-2013-27-2", ("2013", "1-2-2013-27-2")),
                 (u"1 février 2013 à 27 février 2013",
                  (u"1 février 2013 à 27 février 2013", None))]
        for datestr, expected in cases:
            doc = parse(datestr)
            dates = dmr.data.Dates.parse(doc.children[0])
            self.assertEqual(tuple(dates.render(renderer)), expected)


class TestJob(TestCase):
    employerdata = """
| Umbrella Corp.
| 1234 56th St.
| New York, NY 11111
"""
    employer = dmr.data.Contact.parse(parse(employerdata).children[0])

    with_employer_expected = dict(
        employer=employer,
        position="Assistant Manager",
        dates=dmr.data.Dates("March 2012", "Present"),
        description=["Managed assistants.", "Assisted with managing."])
    without_employer_expected = dict(
        employer=employer,
        position=None,
        dates=dmr.data.Dates("March 2012", "Present"),
        description=["Managed assistants.", "Assisted with managing."])

    def _test(self, data, expected, employer=None):
        doc = parse(data)
        job = dmr.data.Job.parse(doc.children[0],
                                 employer=employer).render(renderer)
        self.assertEqual(job2dict(job),
                         expected)

    def test_with_employer(self):
        """ Parse job with employer given as argument """
        data = """
Assistant Manager
~~~~~~~~~~~~~~~~~
March 2012 - Present

* Managed assistants.
* Assisted with managing.
"""
        self._test(data, self.with_employer_expected, employer=self.employer)

    def test_without_employer(self):
        """ Parse job with employer parsed from document """
        data = """
Umbrella Corp.
--------------

| 1234 56th St.
| New York, NY 11111

March 2012 - Present

* Managed assistants.
* Assisted with managing.
"""
        self._test(data, self.without_employer_expected)


class TestSection(TestCase):
    sectionclass = dmr.data.Section

    def _test(self, data, expectedname, expectedcontent):
        doc = parse(data)

        # ensure that the given data is a valid section of this type
        self.assertTrue(self.sectionclass.is_valid(doc.children[0]),
                        "Not a valid %s section" % self.sectionclass.type)

        # ensure that the given data is _not_ a valid section of any
        # other type
        for section in dmr.data.sections:
            if section == self.sectionclass:
                continue
            self.assertFalse(section.is_valid(doc.children[0]),
                             "Unexpectedly a valid %s section" % section.type)

        section = self.sectionclass.parse(doc.children[0]).render(renderer)
        self.assertEqual(section.name, expectedname)
        self._test_data_equality(section, expectedcontent)

    def _test_data_equality(self, section, expected):
        self.assertEqual(section[:], expected)


class TestText(TestSection):
    sectionclass = dmr.data.Text

    def test_title_only(self):
        """ Parse text section with just a title """
        data = """
Test Section
============
"""
        self._test(data, "Test Section", [])

    def test_data(self):
        """ Parse text section with data """
        data = """
Test Section
============

Lorem ipsum dolor sit amet, consectetur adipiscing elit. In quis
libero at tortor pellentesque volutpat non eu mauris. Donec est augue,
elementum id sagittis eget, vehicula ut nisi.

Donec dui purus, cursus tempus aliquam non, suscipit quis
nisi. Aliquam sit amet sagittis est.
"""
        self._test(data, "Test Section",
                   ["Lorem ipsum dolor sit amet, consectetur adipiscing elit. In quis libero at tortor pellentesque volutpat non eu mauris. Donec est augue, elementum id sagittis eget, vehicula ut nisi.",
                    "Donec dui purus, cursus tempus aliquam non, suscipit quis nisi. Aliquam sit amet sagittis est."])


class TestExperience(TestSection):
    sectionclass = dmr.data.Experience
    employerdata1 = """
| Southeast State Tech University
| 1234 56th St.
| New York, NY 11111
"""
    employer1 = dmr.data.Contact.parse(parse(employerdata1).children[0])
    employerdata2 = """
| Northeast Tech State University
| 2345 Address Rd.
| Jersey City, NJ 12121
"""
    employer2 = dmr.data.Contact.parse(parse(employerdata2).children[0])

    def test_with_positions(self):
        """ Parse experience section with position subsections """
        data = """
Test Section
============

Southeast State Tech University
-------------------------------
| 1234 56th St.
| New York, NY 11111

Assistant Manager
~~~~~~~~~~~~~~~~~
1999 - 2004

* Managed assistants.
* Assisted with managing.

Assistant Mangler
~~~~~~~~~~~~~~~~~
2004 - Present

* Mangled assistants.
* Assisted with mangling.

Northeast Tech State University
-------------------------------
| 2345 Address Rd.
| Jersey City, NJ 12121

Assistant to the Assistant's Assistant
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1995-1999

* Meetings, 40 hours a week.
"""
        expected = [
            dmr.data.Job(employer=self.employer1.render(renderer),
                         position="Assistant Manager",
                         dates=dmr.data.Dates("1999", "2004"),
                         description=["Managed assistants.",
                                      "Assisted with managing."]),
            dmr.data.Job(employer=self.employer1.render(renderer),
                         position="Assistant Mangler",
                         dates=dmr.data.Dates("2004", "Present"),
                         description=["Mangled assistants.",
                                      "Assisted with mangling."]),
            dmr.data.Job(employer=self.employer2.render(renderer),
                         position="Assistant to the Assistant's Assistant",
                         dates=dmr.data.Dates("1995", "1999"),
                         description=["Meetings, 40 hours a week."])]
        self._test(data, "Test Section", expected)

    def test_without_positions(self):
        """ Parse experience section without position subsections """
        data = """
Test Section
============

Southeast State Tech University
-------------------------------
| 1234 56th St.
| New York, NY 11111

1999 - 2003

* B.S. in BS

Northeast Tech State University
-------------------------------
| 2345 Address Rd.
| Jersey City, NJ 12121

2003 - 2005

* M.A. in Mastering the Arts
"""
        expected = [dmr.data.Job(employer=self.employer1.render(renderer),
                                 position=None,
                                 dates=dmr.data.Dates("1999", "2003"),
                                 description=["B.S. in BS"]),
                    dmr.data.Job(employer=self.employer2.render(renderer),
                                 position=None,
                                 dates=dmr.data.Dates("2003", "2005"),
                                 description=["M.A. in Mastering the Arts"])]
        self._test(data, "Test Section", expected)

    def _test_data_equality(self, section, expected):
        self.assertEqual([job2dict(j) for j in section],
                         [job2dict(j) for j in expected])


class TestList(TestSection):
    sectionclass = dmr.data.List

    def test(self):
        """ Parse list section """
        data = """
Test Section
============

* Item one.
* Item **two**.
* Item three!
"""
        self._test(data, "Test Section",
                   ["Item one.", "Item two.", "Item three!"])


class TestReferences(TestSection):
    sectionclass = dmr.data.References

    def test(self):
        """ Parse references section """
        contactdata = []
        contactdata.append("""
| Testy McTester
| 1234 56th St.
| New York, NY 11111
""")
        contactdata.append("""
| Test O'Test
| 123 No. Such Rd.
| Faketown, XY 23456
| (123) 456-7890
""")
        sectiondata = """
Test Section
============

%s

%s
""" % tuple(contactdata)
        expected = [dmr.data.Contact.parse(parse(c).children[0])
                    for c in contactdata]
        self._test(sectiondata, "Test Section", expected)


class TestBogusSection(TestCase):
    pass
