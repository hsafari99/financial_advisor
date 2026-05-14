import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_ticker_factory():
    def _make(price, currency):
        mock = MagicMock()
        mock.fast_info.last_price = price
        mock.fast_info.currency = currency
        return mock
    return _make
