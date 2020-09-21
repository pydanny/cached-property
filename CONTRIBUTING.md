# Contributing

Contributions are welcome, and they are greatly appreciated! Every
little bit helps, and credit will always be given.

You can contribute in many ways:

## Types of Contributions

### Report Bugs

Report bugs at https://github.com/pydanny/cached-property/issues.

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

### Fix Bugs

Look through the GitHub issues for bugs. Anything tagged with "bug"
is open to whoever wants to implement it.

### Implement features

Look through the GitHub issues for features. Anything tagged with "feature"
is open to whoever wants to implement it.

### Write Documentation

cached-property could always use more documentation, whether as part of the
official cached-property docs, in docstrings, or even on the web in blog posts,
articles, and such.

### Submit Feedback

The best way to send feedback is to file an issue at https://github.com/pydanny/cached-property/issues.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions are welcome :)

## Get started!

Ready to contribute? Here's how to set up `cached-property` for local development.

1. Fork the `cached-property` repo on GitHub.
2. Clone your fork locally::

    ```bash
    $ git clone git@github.com:your_name_here/cached-property.git
    ```

3. Install your local copy into a virtualenv. Assuming you have virtualenvwrapper installed, this is how you set up your fork for local development:

    ```bash
    $ mkvirtualenv cached-property
    $ cd cached-property/
    $ python setup.py develop
    ```

4. Create a branch for local development:

    ```bash
    $ git checkout -b name-of-your-bugfix-or-feature
    ```

    Now you can make your changes locally.

5. Clean up the formatting (must be running at least Python 3.6):

    ```bash
    $ pip install -U black
    $ black .
    ```

6. When you're done making changes, check that your changes pass the tests, including testing other Python versions with tox:

    ```bash
    $ pytest tests/
    $ tox
    ```

   To get tox, just pip install it into your virtualenv.

7. Commit your changes and push your branch to GitHub::

    ```bash
    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature
    ```

8. Submit a pull request through the GitHub website.

## Pull Request Guidelines

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring, and add the
   feature to the list in README.rst.
3. The pull request should work for Python 2.7, and 3.3, 3.4, 3.5, 3.6 and for PyPy. Check https://travis-ci.org/pydanny/cached-property/pull_requests and make sure that the tests pass for all supported Python versions.

## Tips

To run a subset of tests:

```bash
$ python -m unittest tests.test_cached-property
```
