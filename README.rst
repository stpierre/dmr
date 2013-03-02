=====
 dmr
=====

dmr is **Deduplicate My Resume**.  I've heard that you should update
your resume every two months, but I never do because it's a pain.  I
wanted a way to keep my resume in plain text, in a VCS, but also
generate nice PDFs and stuff.  Enter dmr.

dmr deduplicates your resume.  You write your resume in reStructured
Text.  dmr parses that, and outputs a better format for whatever
purpose you want.  Check out an example at
http://github.com/stpierre/resume

Alternatives
============

I looked into a bunch of alternatives before coding anything.  If all
I had wanted was plain text and HTML, then ``rst2html`` would have
been quite sufficient.  pandoc provides more output formats, but with
both tools I faced the same problem: I wanted layout to be at least
somewhat dicated by the *semantics* of the document, not just the
markup.  So both my "Experience" and "Publications and Presentations"
sections contain enumerated lists, but I wanted them presented
differently.  *And* I wanted them presented in different formats.  (If
all I'd wanted was LaTeX, I could have just written a docutils
Writer.  But I want flexibility!)

Why not Markdown?
-----------------

I chose reStructuredText ultimately because I'm familiar with it.  I
write a lot of Python, and it's the standard Python documentation
language.  If I'd been a Haskell coder, I probably would have used the
pandoc libraries and Markdown.  (I even thought about learning Haskell
for this project, but then I looked at some Haskell code.)

Additionally, Markdown is, and always has been, an HTML-based
language.  It lets you embed HTML, and at least the Python Markdown
parser parses into HTML.  reST has always been a generic lightweight
markup language, and is thus easier to parse into various resulting
formats.  (In my opinion, at least, since you aren't using HTML as a
transitionary language.)

Installing
==========

You can run dmr directly from a ``git clone``, if you want; just set
your ``PATH`` and ``PYTHONPATH`` appropriately.  (A good
``~/.dmr/config`` helps, too.)  Or you can run the included
``setup.py``.  Other than `Genshi <http://genshi.edgewall.org>` (and
argparse on Python 2.6), it doesn't require anything outside of core
Python.  It does require Python 2.6+ or 3.2+, and is primarily
developed, tested, and used on Python 2.7.

Future Possibilities
====================

Eventually I'd like to write an output "format" to sync with
LinkedIn.  Other job searches would be nice, too, but I'm not
currently searching, so those are lower priority.
