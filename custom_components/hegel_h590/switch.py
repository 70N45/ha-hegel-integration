import logging
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        HegelPowerSwitch(data["amp"], entry.data["name"], entry.data["host"]),
    ])


class HegelPowerSwitch(SwitchEntity):
    """Expose Hegel power as a switch for HomeKit."""

    def __init__(self, amp, name: str, host: str):
        self._amp = amp
        self._attr_name = f"{name} Power"
        self._attr_unique_id = f"hegel_h590_{host}_power_switch"
        self._is_on = False

    @property
    def is_on(self) -> bool | None:
        return self._is_on

    async def async_turn_on(self, **kwargs):
        await self._amp.set_power(True)
        self._is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        await self._amp.set_power(False)
        self._is_on = False
        self.async_write_ha_state()

    async def async_update(self):
        try:
            self._is_on = await self._amp.get_power()
        except Exception:
            pass
