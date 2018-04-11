.. image:: https://img.shields.io/badge/License-GPL%20v3-blue.svg
    :target: https://www.gnu.org/licenses/gpl-3.0
    :alt: GPL v3 License

.. image:: https://badge.fury.io/py/duco.ducobox.svg
    :target: https://badge.fury.io/py/duco.ducobox
    :alt: Pypi packaged release

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

Script to monitor a Duco ventilation system.


------------
Installation
------------

Every release is uploaded to pip so it can be installed simply by using pip.

.. code-block:: bash

    # Python2
    pip2 install duco.ducobox

    # Python3
    pip3 install duco.ducobox


-----
Usage
-----

After installation, the python module is available

- as executable, to launch from terminal:

.. code-block:: bash

	ducobox --help

- as python module, to launch from terminal:

.. code-block:: bash

	python -m duco.ducobox --help

- as python module, to import in your script:

.. code-block:: python

	import duco.ducobox as duco

--------------------
Stored configuration
--------------------

The network configuration of your setup is stored in an ini-file. If the network configuration file is not found,
it is created.

The script first tries to find all of the nodes in the network, by executing the *network* command. It creates
objects for all of the found nodes. If nodes are found, the network configuration is saved to the provided
network configuration file.

The network configuration file gives an overview of all the nodes with their specific parameters. These fields
can be adapted for each node:

- *name*: convenience name for the node (any string)
- *blacklist*: flag to blacklist (don't use this node) from the network (True, or False)

The rest of the fields should not be adapted outside the script.

------------
Logging data
------------

The script can log the sampled data to a database.

InfluxDB
========

Data can be logged to an influxDB server, by passing a configuration file to the **--influxdb** option of the script.

Format of this configuration file through an example:

.. code-block::

    [InfluxDB]
    url = localhost
    port = 8086
    user = root
    password = root
    database = ducobox-example

Other databases
===============

The script is setup in a generic way, so adding more kinds of databases should be easy.

-----
Hints
-----

Serial cable details
====================

TODO: provide serial cable details

Allowing non-root user to access serial port (Ubuntu, Linux)
============================================================

1. Add user to dialout group:

.. code-block:: bash

    adduser <username> dialout

2. Use udev to allow users of dialout group to serial device

Content for /etc/udev/rules.d/50-ttyusb.rules

.. code-block:: bash

    SUBSYSTEM=="tty", KERNEL=="ttyUSB0", GROUP="dialout", MODE="0660"

3. Reboot

.. code-block:: bash

    reboot

InfluxDB and Grafana
====================

The script was in first place designed to log sample data to an InfluxDB server. Grafana can
be used as a frontend to create views on the InfluxDB data.

-----------------------
Issues and new Features
-----------------------

In case you have any problems with usage of the plugin, please open an issue
on GitHub. Provide as many valid information as possible, as this will help us
to resolve Issues faster. We would also like to hear your suggestions about new
features which would help your Continuous Integration run better.

----------
Contribute
----------

There is a Contribution guide available if you would like to get involved in
development of the plugin. We encourage anyone to contribute to our repository.
Missing a feature or node, but you're not sure how to start with it? Create an issue.
