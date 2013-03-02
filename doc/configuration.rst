.. include:: defs.rst

.. _configuration:

==============================================
 dmr Configuration and Command Line Arguments
==============================================

.. todo: generate this file automatically

.. automodule:: dmr.config
   :no-members:
   :noindex:

.. _configuration-global:

Global configuration options
============================

All of the options below may be configured in the ``[global]`` section
of the config file.

+------------------+-------------------+---------------------------------------------------------------+-------------------+-----------+
| Command line     | Config file       | Description                                                   | Default           | Values    |
+==================+===================+===============================================================+===================+===========+
| ``--config``     | N/A               | Specify a config file                                         | ``/etc/dmr.conf`` | string    |
| ``-c``           |                   |                                                               |                   |           |
+------------------+-------------------+---------------------------------------------------------------+-------------------+-----------+
| ``--footer``     | ``footer``        | Include a footer in the document with the DMR version         | **False**         | boolean   |
+------------------+-------------------+---------------------------------------------------------------+-------------------+-----------+
| ``--verbose``    | ``verbose``       | Be verbose.  Specify this multiple times on the command line, | ``0``             | int       |
| ``-v``           |                   | or higher values in the config file, to increase verbosity.   |                   |           |
+------------------+-------------------+---------------------------------------------------------------+-------------------+-----------+
| ``--format``     | ``output_format`` | Specify the output format                                     | ``html``          | ``html``, |
| ``-f``           |                   |                                                               |                   | ``json``, |
|                  |                   |                                                               |                   | ``latex`` |
+------------------+-------------------+---------------------------------------------------------------+-------------------+-----------+
| ``--outfile``    | ``outfile``       | Path to the output file.  Specify ``-`` for stdout.           | stdout            | string    |
| ``-o``           |                   |                                                               |                   |           |
+------------------+-------------------+---------------------------------------------------------------+-------------------+-----------+
| First positional | ``infile``        | Path to the input file.  Specify ``-`` for stdin.             | stdin             | string    |
| argument         |                   |                                                               |                   |           |
+------------------+-------------------+---------------------------------------------------------------+-------------------+-----------+

.. _configuration-output:

Output format configuration options
===================================

Individual output formatters can have their own configuration options.
These options are generally set in a section of the config file named
after the output format, although there are some sections (see, e.g.,
:ref:`configuration-genshi`).

.. _configuration-json:

JSON output options
-------------------

This option is configured in the ``[json]`` section of the config file.

+------------------+-------------------+---------------------------------------------------------------+-------------------+-----------+
| Command line     | Config file       | Description                                                   | Default           | Values    |
+==================+===================+===============================================================+===================+===========+
| ``--pretty``     | ``pretty``        | Output prettified JSON                                        | **False**         | boolean   |
+------------------+-------------------+---------------------------------------------------------------+-------------------+-----------+

.. _configuration-genshi:

Genshi output options
---------------------

All output formats that use `Genshi`_ may use the following options.
(Currently, that's just the LaTeX output format.)

+---------------------+-------------------+---------------------------------------------------------------+-------------------+-----------+
| Command line        | Config file       | Description                                                   | Default           | Values    |
+=====================+===================+===============================================================+===================+===========+
| ``--template-path`` | ``template_path`` | Path to Genshi template directory                             | See below         | string    |
|                     | in ``[genshi]``   |                                                               |                   |           |
+---------------------+-------------------+---------------------------------------------------------------+-------------------+-----------+
| ``--template``      | ``template``      | Template to use, relative to the template path                | See below         | string    |
|                     | in output format  |                                                               |                   |           |
|                     | section           |                                                               |                   |           |
+---------------------+-------------------+---------------------------------------------------------------+-------------------+-----------+

The default template path is platform-specific, but will generally be
something like ``/usr/share/dmr/templates``.  ``~/.dmr/templates`` is
also checked, regardless of what you specify for the template path.

The default template is ``<output name>.genshi``, where ``<output
name>`` is the all-lowercase name of the output format.  For the LaTeX
output, for instance, the default template is ``latex.genshi``.

Example
=======

.. code-block:: ini

    [global]
    footer = yes
    verbose = 1
    format = latex
    infile = resume.rst
    outfile = resume.tex

    [json]
    pretty = yes

    [genshi]
    template_path = /usr/share/dmr/templates

    [latex]
    template = myresume.genshi
