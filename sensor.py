"""Support for getting data from websites with scraping."""
import logging

from bs4 import BeautifulSoup
import voluptuous as vol
from vetdata import HUNDDATA_LIST

from homeassistant.components.rest.sensor import RestData
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_NAME,
    CONF_DOG,
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
        vol.Required(CONF_DOG): cv.string,
        vol.Required(CONF_NAME): cv.string,
    }
)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Web scrape sensor."""
    name = config.get(CONF_NAME)
    dog = config.get(CONF_DOG)
    verify_ssl = config.get(CONF_VERIFY_SSL)
    select = config.get(CONF_SELECT)
    attr = config.get(CONF_ATTR)
    index = config.get(CONF_INDEX)
    value_template = config.get(CONF_VALUE_TEMPLATE)
    if value_template is not None:
        value_template.hass = hass

    json_data = json.loads(HUNDDATA_LIST(dog))
    json_data.update()

    if json_data.data is None:
        raise PlatformNotReady

    add_entities(
        [ScrapeSensor(json_data, name, select, attr, index, value_template, unit)], True
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
        self.json_data.update()
        if self.json_data.data is None:
            _LOGGER.error("Unable to retrieve data")
            return

        raw_data = BeautifulSoup(self.json_data.data)
        #raw_data = BeautifulSoup(self.json_data.data, "html.parser")
        _LOGGER.debug(raw_data)

        try:
            if self._attr is not None:
                value = raw_data.select(self._select)[self._index][self._attr]
            else:
                value = raw_data.select(self._select)[self._index].text
            _LOGGER.debug(value)
        except IndexError:
            _LOGGER.error("Unable to extract data from HTML")
            return

        if self._value_template is not None:
            self._state = self._value_template.render_with_possible_json_value(
                value, None
            )
        else:
            self._state = value
