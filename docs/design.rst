
.. _software_design:

===============
Software design
===============

.. _class_diagram:

Class diagram
=============

.. uml::

    @startuml

    DucoInterface "1" o-- "N" DucoNode
    DucoNode "1" o-- "1" DucoInterface
    DucoNode <|-- DucoBox
    DucoNode <|-- DucoBoxSensor
    DucoBoxSensor <|-- DucoBoxHumiditySensor
    DucoBoxSensor <|-- DucoBoxCO2Sensor
    DucoNode <|-- DucoUserControl

    class DucoInterface {
        +__init__(port, cfgfile)
        +bind(port)
        +execute_command(cmd)
        +DucoNode add_node(kind, number, address)
        +find_nodes()
        +load()
        +store()
        +sample()
    }

    class DucoNode {
        +{abstract}{static} KIND = None
        +__init__(number, address)
        +bind(interface)
        +sample()
        +{static}get_subclasses()
    }

    class DucoBox {
        +{static} KIND = 'BOX'
        +__init__(number, address)
    }

    class DucoBoxSensor {
    }

    class DucoBoxHumiditySensor {
        +{static} KIND = 'UCRH'
        +__init__(number, address)
    }

    class DucoBoxCO2Sensor {
        +{static} KIND = 'UCCO2'
        +__init__(number, address)
    }

    class DucoUserControl {
        +{static} KIND = 'UCBAT'
        +__init__(number, address)
    }

    @enduml

Instrument module
=================

.. automodule:: duco.ducobox
    :members:
    :undoc-members:
    :show-inheritance:
