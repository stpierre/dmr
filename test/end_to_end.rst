.. options
   exclude excludeme
   exclude Exclude This Section
.. options=json
   exclude Exclude This Section in JSON
   no-footer
.. options=text
   include Include This Section in Plain Text

================
 Testy O'Tester
================

.. This comment will not be included in any output.

| 1234 No. Such St.
| Nowhere, XX 12345
| cell: +1 (123) 456-7890
| fax: (02) 1234 5678
| not-a-real-address@yahoo.com
| http://myurl.example.com
| http://github.com/stpierre/dmr
| Other data here
| Get some *markup* into the address

Objective
=========

This file tries to test all of the data and input features of dmr in a
single end-to-end test.

Make sure to get another paragraph in here.  And some **markup**.

Experience
==========

Umbrella Corp.
--------------

| 1234 56th St.
| New York, NY 11111

Assistant Manager
~~~~~~~~~~~~~~~~~
March 2012 - Present

* Managed assistants.
* Assisted with managing.

Page Industries
---------------
| 2345 Address Rd.
| Jersey City, NJ 12121

Assistant Mangler
~~~~~~~~~~~~~~~~~
June 2010 - March 2012

* Mangled assistants.
* Assisted with mangling.

Assistant to the Assistant Mangler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
May 2004 - May 2010

* Had a job so cool that it required *markup*.

Job That Will Be Excluded
~~~~~~~~~~~~~~~~~~~~~~~~~
May 2000 - May 2004

.. group excludeme

* This job will be excluded from output.

Education
=========

Southeast State Tech University
-------------------------------
1999 - 2003

* B.S. in BS

Related Skills and Activities
=============================

* Really cool dude.
* Doesn't afraid of anything.

Exclude This Section
====================

This section will always be excluded.

Exclude This Section in JSON
============================

This section will be excluded from JSON output.

References
==========

| Test McTest
| 123 No. Such Rd.
| Faketown, XY 23456
| (123) 456-7890

More References Available Upon Request
======================================

Header with *Markup*
====================

Nothing here.

Include This Section in Plain Text
==================================

.. group excludeme

This section will be included in plain text output.

Exclude This Section By Group
=============================

.. group excludeme

This section will also be excluded.
