
.. _software_design:

===============
Software design
===============

.. _class_diagram:

Class diagram
=============

.. uml::

    @startuml

    DucoNodeParameter <|-- DucoNodeParaGetParameter
    DucoNodeParaGetParameter <|-- DucoNodeHumidityParaGet
    DucoNodeParaGetParameter <|-- DucoNodeCO2ParaGet
    DucoNodeParaGetParameter <|-- DucoNodeTemperatureParaGet
    DucoInterface "1" o-- "N" DucoNode
    DucoInterface "1" o-- "1" DucoDatabase
    DucoNode "1" o-- "N" DucoNodeParameter
    DucoNode "1" o-- "1" DucoInterface

    DucoNode <|-- DucoBox

    DucoNode <|-- DucoNodeWithTemperature
    DucoNode <|-- DucoNodeWithHumidity
    DucoNode <|-- DucoNodeWithCO2

    DucoNode <|-- DucoUserControl
    DucoUserControl <|-- DucoUserControlBattery
    DucoUserControl <|-- DucoUserControlHumiditySensor
    DucoNodeWithTemperature <|-- DucoUserControlHumiditySensor
    DucoNodeWithHumidity <|-- DucoUserControlHumiditySensor
    DucoUserControl <|-- DucoUserControlCO2Sensor
    DucoNodeWithTemperature <|-- DucoUserControlCO2Sensor
    DucoNodeWithHumidity <|-- DucoUserControlCO2Sensor

    DucoNode <|-- DucoValve
    DucoValve <|-- DucoValveHumiditySensor
    DucoNodeWithTemperature <|-- DucoValveHumiditySensor
    DucoNodeWithHumidity <|-- DucoValveHumiditySensor
    DucoValve <|-- DucoValveCO2Sensor
    DucoNodeWithTemperature <|-- DucoValveCO2Sensor
    DucoNodeWithCO2 <|-- DucoValveCO2Sensor

    DucoNode <|-- DucoSwitch

    DucoNodeWithTemperature <|-- DucoGrille

    DucoDatabase <|-- InfluxDb

    class DucoNodeParameter {
        +__init__(name, unit, scaling)
        +set_value(value)
        +get_value()
    }

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

    class DucoDatabase {
        +__init__()
        +store_sample(node, measurement, value)
    }

    class InfluxDb {
        +__init__(url, port, user, password, dbname)
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

    class DucoUserControl {
        +{static} KIND = 'UC'
    }

    class DucoUserControlBattery {
        +{static} KIND = 'UCBAT'
    }

    class DucoUserControlHumiditySensor {
        +{static} KIND = 'UCRH'
    }

    class DucoUserControlCO2Sensor {
        +{static} KIND = 'UCCO2'
    }

    class DucoValve {
        +{static} KIND = 'VLV'
    }

    class DucoValveHumiditySensor {
        +{static} KIND = 'VLVRH'
    }

    class DucoValveCO2Sensor {
        +{static} KIND = 'VLVCO2'
    }

    class DucoSwitch {
        +{static} KIND = 'SWITCH'
    }

    class DucoGrille {
        +{static} KIND = 'CLIMA'
    }

    @enduml

Instrument module
=================

.. automodule:: duco.ducobox
    :members:
    :undoc-members:
    :show-inheritance:
