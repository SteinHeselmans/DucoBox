
.. _software_design:

===============
Software design
===============

.. _class_diagram:

Class diagram
=============

.. uml::

    @startuml

    DucoNode <|-- DucoBox
    DucoBox o-- DucoNode

    class DucoBox {
        +__init__(tty)
        +get_nodes()
    }

    class DucoNode {
        +__init__(tty)
    }

    @enduml

Instrument module
=================

.. automodule:: duco.ducobox
    :members:
    :undoc-members:
    :show-inheritance:
