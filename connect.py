"""Connect parameters for Hunddata"""
import logging
import requests
import json

from homeassistant.const import (
    CONF_DOG,
    CONF_NAME,
)
from vetdata import HUNDDATA_LIST

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_DOG): cv.string,
        vol.Required(CONF_NAME): cv.string,
    }
)

_LOGGER = logging.getLogger(__name__)

class Hunddata:
    data = None

    @staticmethod
    def do_api_request():
        """Do API request."""
        json_data = json.loads(HUNDDATA_LIST.json_data)
        return json_data
