import logging
from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        HegelVolumeFan(data["amp"], entry.data["name"], entry.data["host"]),
    ])


class HegelVolumeFan(FanEntity):
    """Expose Hegel volume as a fan speed percentage for HomeKit."""

    _attr_supported_features = (
        FanEntityFeature.SET_SPEED
        | FanEntityFeature.TURN_ON
        | FanEntityFeature.TURN_OFF
    )
    _attr_speed_count = 100

    def __init__(self, amp, name: str, host: str):
        self._amp = amp
        self._attr_name = f"{name} Volume"
        self._attr_unique_id = f"hegel_h590_{host}_volume_fan"
        self._is_on = False
        self._percentage = 0

    @property
    def is_on(self) -> bool | None:
        return self._is_on

    @property
    def percentage(self) -> int | None:
        return self._percentage

    async def async_turn_on(self, percentage=None, preset_mode=None, **kwargs):
        await self._amp.set_power(True)
        self._is_on = True
        if percentage is not None:
            await self._amp.set_volume(percentage)
            self._percentage = percentage
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        await self._amp.set_power(False)
        self._is_on = False
        self._percentage = 0
        self.async_write_ha_state()

    async def async_set_percentage(self, percentage: int):
        if percentage == 0:
            await self.async_turn_off()
            return
        await self._amp.set_volume(percentage)
        self._percentage = percentage
        if not self._is_on:
            await self._amp.set_power(True)
            self._is_on = True
        self.async_write_ha_state()

    async def async_update(self):
        try:
            self._is_on = await self._amp.get_power()
            self._percentage = await self._amp.get_volume() if self._is_on else 0
        except Exception:
            pass
