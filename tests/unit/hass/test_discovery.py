import pytest

from shine2mqtt.hass.config import DeviceConfig, HassDiscoveryConfig
from shine2mqtt.hass.discovery import MqttDiscoveryBuilder


@pytest.fixture
def config():
    return HassDiscoveryConfig(
        base_topic="solar",
        availability_topic="solar/state",
        prefix_topic="homeassistant",
        inverter=DeviceConfig(brand="Growatt", model="MIC 3000TL-X"),
        datalogger=DeviceConfig(brand="Growatt", model="ShineWiFi-X"),
    )


@pytest.fixture
def builder(config, sensor_map):
    return MqttDiscoveryBuilder(
        config=config,
        datalogger_sensor_map=sensor_map,
        inverter_sensor_map=sensor_map,
    )


@pytest.fixture
def sensor_map():
    return {
        "temperature": {
            "name": "Temperature",
            "icon": "mdi:thermometer",
            "device_class": "temperature",
            "unit_of_measurement": "°C",
        },
        "status": {
            "name": "Status",
            "icon": "mdi:information",
            "entity_category": "diagnostic",
        },
        "simple": {
            "name": "Simple Sensor",
            "icon": "mdi:gauge",
        },
    }


class TestMqttDiscoveryBuilder:
    def test_discovery_origin_contains_package_info(self):
        assert MqttDiscoveryBuilder.DISCOVERY_ORIGIN == {
            "name": "shine2mqtt",
            "sw_version": "0.0.2",
            "support_url": "https://github.com/bremme/shine2mqtt",
        }


class TestBuildDataloggerDiscoveryMessage:
    def test_build_datalogger_discovery_message(self, builder):
        result = builder.build_datalogger_discovery_message("1.0.0", "ABC123")

        assert result == {
            "availability_topic": "solar/state",
            "device": {
                "identifiers": ["growatt_shinewifi_x", "ABC123"],
                "manufacturer": "Growatt",
                "model": "ShineWiFi-X",
                "name": "Growatt Shinewifi-X",
                "sw_version": "1.0.0",
                "serial_number": "ABC123",
            },
            "origin": MqttDiscoveryBuilder.DISCOVERY_ORIGIN,
            "components": {
                "temperature": {
                    "platform": "sensor",
                    "name": "Temperature",
                    "icon": "mdi:thermometer",
                    "value_template": "{{ value_json.value }}",
                    "unique_id": "temperature",
                    "state_topic": "solar/datalogger/sensor/temperature",
                    "device_class": "temperature",
                    "unit_of_measurement": "°C",
                },
                "status": {
                    "platform": "sensor",
                    "name": "Status",
                    "icon": "mdi:information",
                    "value_template": "{{ value_json.value }}",
                    "unique_id": "status",
                    "state_topic": "solar/datalogger/sensor/status",
                    "entity_category": "diagnostic",
                },
                "simple": {
                    "platform": "sensor",
                    "name": "Simple Sensor",
                    "icon": "mdi:gauge",
                    "value_template": "{{ value_json.value }}",
                    "unique_id": "simple",
                    "state_topic": "solar/datalogger/sensor/simple",
                },
            },
        }


class TestBuildInverterDiscoveryMessage:
    def test_build_inverter_discovery_message(self, builder):
        result = builder.build_inverter_discovery_message("1.2.3", "INV789")

        assert result == {
            "availability_topic": "solar/state",
            "device": {
                "identifiers": ["growatt_mic_3000tl_x", "INV789"],
                "manufacturer": "Growatt",
                "model": "MIC 3000TL-X",
                "name": "Growatt Mic 3000Tl-X",
                "sw_version": "1.2.3",
                "serial_number": "INV789",
                "via_device": "growatt_shinewifi_x",
            },
            "origin": MqttDiscoveryBuilder.DISCOVERY_ORIGIN,
            "components": {
                "temperature": {
                    "platform": "sensor",
                    "name": "Temperature",
                    "icon": "mdi:thermometer",
                    "value_template": "{{ value_json.value }}",
                    "unique_id": "temperature",
                    "state_topic": "solar/inverter/sensor/temperature",
                    "device_class": "temperature",
                    "unit_of_measurement": "°C",
                },
                "status": {
                    "platform": "sensor",
                    "name": "Status",
                    "icon": "mdi:information",
                    "value_template": "{{ value_json.value }}",
                    "unique_id": "status",
                    "state_topic": "solar/inverter/sensor/status",
                    "entity_category": "diagnostic",
                },
                "simple": {
                    "platform": "sensor",
                    "name": "Simple Sensor",
                    "icon": "mdi:gauge",
                    "value_template": "{{ value_json.value }}",
                    "unique_id": "simple",
                    "state_topic": "solar/inverter/sensor/simple",
                },
            },
        }


class TestBuildDiscoveryTopics:
    def test_build_inverter_discovery_topic(self, builder):
        result = builder.build_inverter_discovery_topic()
        assert result == "homeassistant/device/growatt_mic_3000tl_x/config"

    def test_build_datalogger_discovery_topic(self, builder):
        result = builder.build_datalogger_discovery_topic()
        assert result == "homeassistant/device/growatt_shinewifi_x/config"

    def test_uses_custom_prefix_topic(self, sensor_map):
        config = HassDiscoveryConfig(
            prefix_topic="ha",
            inverter=DeviceConfig(brand="Test", model="Inverter"),
            datalogger=DeviceConfig(brand="Test", model="Logger"),
        )
        builder = MqttDiscoveryBuilder(config, sensor_map, sensor_map)

        assert builder.build_inverter_discovery_topic() == "ha/device/test_inverter/config"
        assert builder.build_datalogger_discovery_topic() == "ha/device/test_logger/config"
