
.. _software_design:

===============
Software design
===============

.. _class_diagram:

Class diagram
=============

.. uml::

    @startuml

    DucoInterface o-- DucoNode
    DucoNode <|-- DucoBox
    DucoNode <|-- DucoBoxSensor
    DucoBoxSensor <|-- DucoBoxHumiditySensor
    DucoBoxSensor <|-- DucoBoxCO2Sensor
    DucoNode <|-- DucoUserControl

    class DucoInterface {
        +__init__(port, cfgfile)
        +get_nodes()
        +load()
        +store()
    }

    class DucoNode {
        +{abstract}{static} TYPE = None
        +__init__(number, address)
    }

    class DucoBox {
        +{static} TYPE = 'BOX'
        +__init__(number, address)
    }

    class DucoBoxSensor {
    }

    class DucoBoxHumiditySensor {
        +{static} TYPE = 'UCRH'
        +__init__(number, address)
    }

    class DucoBoxCO2Sensor {
        +{static} TYPE = 'UCCO2'
        +__init__(number, address)
    }

    class DucoUserControl {
        +{static} TYPE = 'UCBAT'
        +__init__(number, address)
    }

    @enduml

Instrument module
=================

.. automodule:: duco.ducobox
    :members:
    :undoc-members:
    :show-inheritance:
