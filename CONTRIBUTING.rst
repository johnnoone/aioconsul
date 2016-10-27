Contributing
============

The main repository is hosted on https://lab.errorist.xyz/aio/aioconsul and
is mirrored into Github https://github.com/johnnoone/aioconsul.

We'd love for you to contribute to our source code and to make AIOConsul_ even
better than it is today! Here are the guidelines we'd like you to follow:


Got a Question or Problem?
~~~~~~~~~~~~~~~~~~~~~~~~~~

If you have questions about how to use AIOConsul, please send directly an
email to main commiters of repository.


Found an Issue?
~~~~~~~~~~~~~~~

If you find a bug in the source code or a mistake in the documentation, you
can help us by submitting an issue to our `GitHub Repository`_.
Even better you can submit a Pull Request with a fix.


Want a Feature?
~~~~~~~~~~~~~~~

You can request a new feature by submitting an issue to our
`GitHub Repository`_. If you would like to implement a new feature then
consider what kind of change it is:

* **Major Changes** that you wish to contribute to the project should be
  discussed first so that we can better coordinate our efforts, prevent
  duplication of work, and help you to craft the change so that it is
  successfully accepted into the project.
* **Small** Changes can be crafted and submitted to the `GitHub Repository`_
  as a Pull Request.


Want a Doc Fix?
---------------

If you want to help improve the docs, it's a good idea to let others know what
you're working on to minimize duplication of effort. Create a new issue (or
comment on a related existing one) to let others know what you're working on.

For large fixes, please build and test the documentation before submitting the
PR to be sure you haven't accidentally introduced any layout or formatting
issues.

If you're just making a small change, don't worry about filing an issue first.
Use the friendly blue "Improve this doc" button at the top right of the doc
page to fork the repository in-place and make a quick change on the fly.


Coding Rules
------------

To ensure consistency throughout the source code, keep these rules in mind as
you are working:

* All features or bug fixes must be tested.
* All public API methods must be documented using RestructuredText in
  conjonction of Napoleon_.
* All code msut be linted with flake8_

.. _`GitHub Repository`: https://github.com/johnnoone/aioconsul
.. _flake8: https://pypi.python.org/pypi/flake8
.. _Napoleon: https://pypi.python.org/pypi/sphinxcontrib-napoleon
.. _AIOConsul: http://aio.errorist.io/aioconsul
