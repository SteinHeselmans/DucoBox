
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
        +__init__(port, cfgfile)
        +get_nodes()
        +load()
        +store()
    }

    class DucoNode {
        +__init__(name, address)
    }

    @enduml

Instrument module
=================

.. automodule:: duco.ducobox
    :members:
    :undoc-members:
    :show-inheritance:
