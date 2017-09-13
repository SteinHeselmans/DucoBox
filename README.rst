.. image:: https://img.shields.io/hexpm/l/plug.svg
    :target: http://www.apache.org/licenses/LICENSE-2.0
    :alt: Apache2 License

.. image:: https://travis-ci.org/SteinHeselmans/DucoBox.svg?branch=master
    :target: https://travis-ci.org/SteinHeselmans/DucoBox
    :alt: Build status

.. image:: https://codecov.io/gh/SteinHeselmans/DucoBox/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/SteinHeselmans/DucoBox
    :alt: Code Coverage

.. image:: https://codeclimate.com/github/SteinHeselmans/DucoBox/badges/gpa.svg
    :target: https://codeclimate.com/github/SteinHeselmans/DucoBox
    :alt: Code Climate Status

.. image:: https://codeclimate.com/github/SteinHeselmans/DucoBox/badges/issue_count.svg
    :target: https://codeclimate.com/github/SteinHeselmans/DucoBox
    :alt: Issue Count

.. image:: https://requires.io/github/SteinHeselmans/DucoBox/requirements.svg?branch=master
    :target: https://requires.io/github/SteinHeselmans/DucoBox/requirements/?branch=master
    :alt: Requirements Status

.. image:: https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat
    :target: https://github.com/SteinHeselmans/DucoBox/issues
    :alt: Contributions welcome


=======
DucoBox
=======

Script to monitor a DucoBox ventilation system.


============
Installation
============

Every release is uploaded to pip so it can be installed simply by using pip.

.. code-block:: bash

    # Python2
    pip2 install duco.ducobox

    # Python3
    pip3 install duco.ducobox

You can find more details in `Installation guide <docs/installation.rst>`_

=====
Usage
=====

=====
Hints
=====

Allowing non-root user to access serial port (Ubuntu, Linux)
============================================================

1. Add user to dialout group:

::

    adduser <username> dialout

2. Use udev to allow users of dialout group to serial device

Content for /etc/udev/rules.d/50-ttyusb.rules

::

    SUBSYSTEM=="tty", KERNEL=="ttyUSB0", GROUP="dialout", MODE="0660"

3. Reboot

::

    reboot 

=======================
Issues and new Features
=======================

In case you have any problems with usage of the plugin, please open an issue
on GitHub. Provide as many valid information as possible, as this will help us
to resolve Issues faster. We would also like to hear your suggestions about new
features which would help your Continuous Integration run better.

==========
Contribute
==========

There is a Contribution guide available if you would like to get involved in
development of the plugin. We encourage anyone to contribute to our repository.

