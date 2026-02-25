import pytest

from shine2mqtt.growatt.protocol.base.decoder_registry import DecoderRegistry
from shine2mqtt.growatt.protocol.constants import FunctionCode
from shine2mqtt.growatt.protocol.frame.factory import FrameFactory


class TestBidirectionalProtocol:
    @pytest.fixture
    def server_decoder(self):
        """Server decoder for messages FROM client."""
        return FrameFactory.server_decoder()

    @pytest.fixture
    def client_decoder(self):
        """Client decoder for messages FROM server."""
        return FrameFactory.client_decoder()

    def test_server_registry_has_correct_decoders(self):
        """Server should decode client requests."""
        registry = DecoderRegistry.server()

        announce_decoder = registry.get_decoder(FunctionCode.ANNOUNCE)
        assert announce_decoder.__class__.__name__ == "AnnounceRequestDecoder"
        data_decoder = registry.get_decoder(FunctionCode.DATA)
        assert data_decoder.__class__.__name__ == "DataRequestDecoder"

        ping_decoder = registry.get_decoder(FunctionCode.PING)
        assert ping_decoder.__class__.__name__ == "PingRequestDecoder"

        config_decoder = registry.get_decoder(FunctionCode.GET_CONFIG)
        assert config_decoder.__class__.__name__ == "GetConfigResponseDecoder"

    def test_client_registry_has_correct_decoders(self):
        """Client should decode server responses."""
        registry = DecoderRegistry.client()

        announce_decoder = registry.get_decoder(FunctionCode.ANNOUNCE)
        assert announce_decoder.__class__.__name__ == "AckMessageResponseDecoder"

        data_decoder = registry.get_decoder(FunctionCode.DATA)
        assert data_decoder.__class__.__name__ == "AckMessageResponseDecoder"

        ping_decoder = registry.get_decoder(FunctionCode.PING)
        assert ping_decoder.__class__.__name__ == "PingRequestDecoder"

        config_decoder = registry.get_decoder(FunctionCode.GET_CONFIG)
        assert config_decoder.__class__.__name__ == "GetConfigRequestDecoder"

    def test_announce_function_code_decodes_differently(self):
        server_registry = DecoderRegistry.server()
        client_registry = DecoderRegistry.client()

        server_decoder = server_registry.get_decoder(FunctionCode.ANNOUNCE)
        client_decoder = client_registry.get_decoder(FunctionCode.ANNOUNCE)

        assert server_decoder.__class__.__name__ == "AnnounceRequestDecoder"
        assert client_decoder.__class__.__name__ == "AckMessageResponseDecoder"

    def test_get_config_function_code_decodes_differently(self):
        server_registry = DecoderRegistry.server()
        client_registry = DecoderRegistry.client()

        server_decoder = server_registry.get_decoder(FunctionCode.GET_CONFIG)
        client_decoder = client_registry.get_decoder(FunctionCode.GET_CONFIG)

        assert server_decoder.__class__.__name__ == "GetConfigResponseDecoder"
        assert client_decoder.__class__.__name__ == "GetConfigRequestDecoder"
