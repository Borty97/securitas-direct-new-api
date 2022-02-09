"""Securitas direct sentinel sensor."""
from datetime import timedelta

from homeassistant.helpers.entity import DeviceInfo

from .securitas_direct_new_api.dataTypes import (
    AirQuality,
    Sentinel,
    Service,
)
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.const import CONF_PASSWORD, PERCENTAGE, TEMP_CELSIUS
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DOMAIN, SecuritasHub

SCAN_INTERVAL = timedelta(minutes=30)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up MELCloud device sensors based on config_entry."""
    client: SecuritasHub = entry.data[CONF_PASSWORD]
    sensors = []

    for item in client.sentinel_services:
        sentinel_data: Sentinel = await client.session.get_sentinel_data(
            item.installation, item
        )
        sensors.append(SentinelTemperature(sentinel_data, item, client))
        sensors.append(SentinelHumidity(sentinel_data, item, client))

        air_quality: AirQuality = await client.session.get_air_quality_data(
            item.installation, item
        )
        sensors.append(SentinelAirQuality(air_quality, sentinel_data, item, client))
    async_add_entities(sensors, True)


class SentinelTemperature(SensorEntity):
    """Sentinel temperature sensor."""

    def __init__(
        self, sentinel: Sentinel, service: Service, client: SecuritasHub
    ) -> None:
        """Init the component."""
        self._update_sensor_data(sentinel)
        self._attr_unique_id = sentinel.alias + "_temperature_" + str(service.id)
        self._attr_name = "Temperature " + sentinel.alias.lower().capitalize()
        self._sentinel: Sentinel = sentinel
        self._service: Service = service
        self._client: SecuritasHub = client
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._attr_unique_id)},
            manufacturer="Temperature Sensor",
            model=service.id_service,
            name=service.description,
        )

    async def update(self):
        """Update the status of the alarm based on the configuration."""
        sentinel_data: Sentinel = await self._client.session.get_sentinel_data(
            self._service.installation, self._service
        )
        self._update_sensor_data(sentinel_data)

    def _update_sensor_data(self, sentinel: Sentinel):
        self._attr_device_class = SensorDeviceClass.TEMPERATURE
        self._attr_native_value = sentinel.temperature
        self._attr_native_unit_of_measurement = TEMP_CELSIUS


class SentinelHumidity(SensorEntity):
    """Sentinel Humidity sensor."""

    def __init__(
        self, sentinel: Sentinel, service: Service, client: SecuritasHub
    ) -> None:
        """Init the component."""
        self._update_sensor_data(sentinel)
        self._attr_unique_id = sentinel.alias + "_humidity_" + str(service.id)
        self._attr_name = "Humidity " + sentinel.alias.lower().capitalize()
        self._sentinel: Sentinel = sentinel
        self._service: Service = service
        self._client: SecuritasHub = client

    async def update(self):
        """Update the status of the alarm based on the configuration."""
        sentinel_data: Sentinel = await self._client.session.get_sentinel_data(
            self._service.installation, self._service
        )
        self._update_sensor_data(sentinel_data)

    def _update_sensor_data(self, sentinel: Sentinel):
        self._attr_device_class = SensorDeviceClass.HUMIDITY
        self._attr_native_value = sentinel.humidity
        self._attr_native_unit_of_measurement = PERCENTAGE


class SentinelAirQuality(SensorEntity):
    """Sentinel Humidity sensor."""

    def __init__(
        self,
        air_quality: AirQuality,
        sentinel: Sentinel,
        service: Service,
        client: SecuritasHub,
    ) -> None:
        """Init the component."""
        self._update_sensor_data(air_quality)
        self._attr_unique_id = sentinel.alias + "airquality_" + str(service.id)
        self._attr_name = "Air Quality " + sentinel.alias.lower().capitalize()
        self._air_quality: AirQuality = air_quality
        self._service: Service = service
        self._client: SecuritasHub = client

    async def update(self):
        """Update the status of the alarm based on the configuration."""
        air_quality: Sentinel = await self._client.session.get_air_quality_data(
            self._service.installation, self._service
        )
        self._update_sensor_data(air_quality)

    def _update_sensor_data(self, air_quality: AirQuality):
        self._attr_device_class = SensorDeviceClass.AQI
        self._attr_native_value = air_quality.value
