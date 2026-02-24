import pytest

from shine2mqtt.adapters.hass.config import DeviceConfig, HassDiscoveryConfig
from shine2mqtt.adapters.hass.discovery import HassDiscoveryPayloadBuilder
from shine2mqtt.adapters.hass.map import INVERTER_SENSOR_MAP
from shine2mqtt.domain.models.datalogger import DataLogger


@pytest.fixture
def config() -> HassDiscoveryConfig:
    return HassDiscoveryConfig(
        base_topic="solar",
        availability_topic="solar/state",
        prefix_topic="homeassistant",
        inverter=DeviceConfig(brand="Growatt", model="MIC 3000TL-X"),
        datalogger=DeviceConfig(brand="Growatt", model="ShineWiFi-X"),
    )


@pytest.fixture
def builder(config, sensor_map) -> HassDiscoveryPayloadBuilder:
    return HassDiscoveryPayloadBuilder(
        config=config,
        datalogger_sensor_map=sensor_map,
        inverter_sensor_map=sensor_map,
    )


@pytest.fixture
def sensor_map() -> dict[str, dict[str, str]]:
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


@pytest.fixture
def real_sensor_map():
    return INVERTER_SENSOR_MAP


class TestMqttDiscoveryBuilder:
    def test_discovery_origin_contains_package_info(self):
        assert HassDiscoveryPayloadBuilder.DISCOVERY_ORIGIN == {
            "name": "shine2mqtt",
            "sw_version": "0.1.0",
            "support_url": "https://github.com/bremme/shine2mqtt",
        }


class TestMqttDiscoveryBuilderDiscoveryMessage:
    def test_build_datalogger_discovery_message(self, builder: HassDiscoveryPayloadBuilder):
        datalogger = DataLogger(
            serial="ABC123",
            sw_version="1.2.3",
            hw_version="4.5.6",
            protocol_id=0,
            unit_id=1,
            ip_address="192.168.1.100",
            mac_address="00:11:22:33:44:55",
        )
        result = builder.build_datalogger_discovery_message(datalogger)

        assert result == {
            "availability_topic": "solar/state",
            "device": {
                "identifiers": ["growatt_shinewifi_x", "ABC123"],
                "manufacturer": "Growatt",
                "model": "ShineWiFi-X",
                "name": "Growatt Shinewifi-X",
                "sw_version": "1.2.3",
                "hw_version": "4.5.6",
                "connections": [["ip", "192.168.1.100"], ["mac", "00:11:22:33:44:55"]],
                "configuration_url": "http://192.168.1.100",
                "serial_number": "ABC123",
            },
            "origin": HassDiscoveryPayloadBuilder.DISCOVERY_ORIGIN,
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

    def test_build_inverter_discovery_message(self, builder: HassDiscoveryPayloadBuilder):
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
            "origin": HassDiscoveryPayloadBuilder.DISCOVERY_ORIGIN,
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

    def test_build_inverter_discovery_message_with_real_sensor_map(
        self, config: HassDiscoveryConfig, real_sensor_map: dict[str, dict[str, str]]
    ):
        builder = HassDiscoveryPayloadBuilder(
            config=config,
            datalogger_sensor_map=real_sensor_map,
            inverter_sensor_map=real_sensor_map,
        )

        result = builder.build_inverter_discovery_message("1.2.3", "INV789")

        assert "components" in result

        components = result["components"]

        assert len(components) == len(real_sensor_map)
        assert "power_ac" in components
        assert "inverter_serial" in components

        # Verify component structure with real sensor
        power_ac = components["power_ac"]
        assert power_ac["platform"] == "sensor"
        assert power_ac["state_topic"] == "solar/inverter/sensor/power_ac"
        assert power_ac["device_class"] == "power"
        assert power_ac["unit_of_measurement"] == "W"

        # Verify optional fields work
        inverter_serial = components["inverter_serial"]
        assert "device_class" not in inverter_serial
        assert "unit_of_measurement" not in inverter_serial


class TestMqttDiscoveryBuilderTopics:
    def test_build_inverter_discovery_topic(self, builder: HassDiscoveryPayloadBuilder):
        result = builder.build_inverter_discovery_topic()
        assert result == "homeassistant/device/growatt_mic_3000tl_x/config"

    def test_build_datalogger_discovery_topic(self, builder: HassDiscoveryPayloadBuilder):
        result = builder.build_datalogger_discovery_topic()
        assert result == "homeassistant/device/growatt_shinewifi_x/config"

    def test_uses_custom_prefix_topic(self, sensor_map: dict[str, dict[str, str]]):
        config = HassDiscoveryConfig(
            prefix_topic="ha",
            inverter=DeviceConfig(brand="Test", model="Inverter"),
            datalogger=DeviceConfig(brand="Test", model="Logger"),
        )
        builder = HassDiscoveryPayloadBuilder(config, sensor_map, sensor_map)

        assert builder.build_inverter_discovery_topic() == "ha/device/test_inverter/config"
        assert builder.build_datalogger_discovery_topic() == "ha/device/test_logger/config"
