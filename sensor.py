"""Support for getting data from websites with scraping."""
import logging
import json
import requests
from bs4 import BeautifulSoup
import voluptuous as vol
from custom_components.hunddata.vetdata import hunddata_list


from homeassistant.components.rest.sensor import RestData
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_AUTHENTICATION,
    CONF_HEADERS,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_RESOURCE,
    CONF_UNIT_OF_MEASUREMENT,
    CONF_USERNAME,
    CONF_VALUE_TEMPLATE,
    CONF_VERIFY_SSL,
    HTTP_BASIC_AUTHENTICATION,
    HTTP_DIGEST_AUTHENTICATION,
)
from homeassistant.exceptions import PlatformNotReady
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)

CONF_ATTR = "attribute"
CONF_SELECT = "select"
CONF_INDEX = "index"

DEFAULT_NAME = "Hunddata"
DEFAULT_VERIFY_SSL = True

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_RESOURCE): cv.string,
        vol.Required(CONF_SELECT): cv.string,
        vol.Optional(CONF_ATTR): cv.string,
        vol.Optional(CONF_INDEX, default=0): cv.positive_int,
        vol.Optional(CONF_AUTHENTICATION): vol.In(
            [HTTP_BASIC_AUTHENTICATION, HTTP_DIGEST_AUTHENTICATION]
        ),
        vol.Optional(CONF_HEADERS): vol.Schema({cv.string: cv.string}),
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_PASSWORD): cv.string,
        vol.Optional(CONF_UNIT_OF_MEASUREMENT): cv.string,
        vol.Optional(CONF_USERNAME): cv.string,
        vol.Optional(CONF_VALUE_TEMPLATE): cv.template,
        vol.Optional(CONF_VERIFY_SSL, default=DEFAULT_VERIFY_SSL): cv.boolean,
    }
)


def setup_platform(hass, config, add_entities, discovery_info=None):
    _LOGGER.debug("Adding sensor component: Hunddata ...")
    """Set up the  sensor."""
    name = config.get(CONF_NAME)
    verify_ssl = config.get(CONF_VERIFY_SSL)
    select = config.get(CONF_SELECT)
    attr = config.get(CONF_ATTR)
    index = config.get(CONF_INDEX)
    unit = "hund"
    value_template = config.get(CONF_VALUE_TEMPLATE)
    if value_template is not None:
        value_template.hass = hass

    json_data = hunddata_list(select)
    #json_data.update()
    #if json_data.data is None:
    #    raise PlatformNotReady

    add_entities(
        [Hunddata(json_data, name, select, attr, index, value_template, unit)], True
    )


class Hunddata(Entity):
    """Representation of a web scrape sensor."""

    def __init__(self, json_data, name, select, attr, index, value_template, unit):
        """Initialize a web scrape sensor."""
        self.json_data = json_data
        self._name = name
        self._state = None
        self._select = select
        self._attr = attr
        self._index = index
        self._value_template = value_template
        self._unit_of_measurement = unit

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def unit_of_measurement(self):
        """Return the unit the value is expressed in."""
        return "hund" #self._unit_of_measurement

    @property
    def state(self):
        """Return the state of the device."""
        return self._state

    def update(self):
        """Get the latest data from the source and updates the state."""
        read = hunddata_list(self._select)
        self.json_data = json.loads(read)

        if self.json_data is None:
            _LOGGER.error("Unable to retrieve data")
            return

        #raw_data = BeautifulSoup(self.json_data)
        #raw_data = BeautifulSoup(self.json_data.data, "html.parser")
        _LOGGER.debug(self.json_data)

        self._state = self.json_data["Datum"]
