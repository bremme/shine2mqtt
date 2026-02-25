import pytest

from shine2mqtt.adapters.hass.config import DeviceConfig, HassDiscoveryConfig


class TestDeviceConfig:
    def test_create_with_defaults(self):
        device = DeviceConfig()

        assert device.brand == "Growatt"
        assert device.model == "Unknown"
        assert device.device_id == "growatt_unknown"
        assert device.name == "Growatt Unknown"

    def test_create_with_custom_values(self):
        device = DeviceConfig(brand="SolarEdge", model="SE7600H")

        assert device.brand == "SolarEdge"
        assert device.model == "SE7600H"

    @pytest.mark.parametrize(
        "brand,model,expected_id",
        [
            ("My Brand", "Super Model", "my_brand_super_model"),
            ("Solar-Edge", "SE-7600", "solar_edge_se_7600"),
            ("Brand|Name", "Model|Type", "brand_name_model_type"),
            ("Brand - Name | Type", "Model-123 | Pro", "brand_name_type_model_123_pro"),
            ("  Growatt  ", "  MIC 3000TL-X  ", "growatt_mic_3000tl_x"),
            ("UPPERCASE", "lowercase", "uppercase_lowercase"),
            ("", "", "_"),
            ("---", "|||", "___"),
        ],
    )
    def test_device_id_normalization(self, brand, model, expected_id):
        device = DeviceConfig(brand=brand, model=model)
        assert device.device_id == expected_id

    def test_name_title_cases_values(self):
        device = DeviceConfig(brand="growatt", model="mic 3000tl-x")
        assert device.name == "Growatt Mic 3000Tl-X"


class TestHassDiscoveryConfig:
    def test_create_with_defaults(self):
        config = HassDiscoveryConfig()

        assert config.enabled is True
        assert config.base_topic == "solar"
        assert config.availability_topic == "solar/state"
        assert config.prefix_topic == "homeassistant"
        assert config.inverter.brand == "Growatt"
        assert config.datalogger.brand == "Growatt"

    def test_create_with_custom_values(self):
        config = HassDiscoveryConfig(
            enabled=False,
            base_topic="energy",
            availability_topic="energy/status",
            prefix_topic="ha",
        )

        assert config.enabled is False
        assert config.base_topic == "energy"
        assert config.availability_topic == "energy/status"
        assert config.prefix_topic == "ha"

    def test_create_with_custom_devices(self):
        inverter = DeviceConfig(brand="SolarEdge", model="SE7600H")
        datalogger = DeviceConfig(brand="Custom", model="Logger-1")

        config = HassDiscoveryConfig(inverter=inverter, datalogger=datalogger)

        assert config.inverter.brand == "SolarEdge"
        assert config.inverter.model == "SE7600H"
        assert config.datalogger.brand == "Custom"
        assert config.datalogger.model == "Logger-1"
