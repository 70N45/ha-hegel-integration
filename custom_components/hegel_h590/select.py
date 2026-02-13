import logging
from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        HegelSourceSelect(data["amp"], entry.data["name"], entry.data["host"], data["sources"]),
    ])


class HegelSourceSelect(SelectEntity):
    """Expose Hegel input source as a select entity for HomeKit."""

    def __init__(self, amp, name: str, host: str, sources: dict):
        self._amp = amp
        self._attr_name = f"{name} Input"
        self._attr_unique_id = f"hegel_h590_{host}_input_select"
        self._source_map = dict(sources)
        self._reverse_source_map = {v: k for k, v in sources.items()}
        self._attr_options = list(sources.keys())
        self._attr_current_option = None

    @property
    def current_option(self) -> str | None:
        return self._attr_current_option

    async def async_select_option(self, option: str):
        source_id = self._source_map.get(option)
        if source_id is not None:
            await self._amp.set_source(source_id)
            self._attr_current_option = option
            self.async_write_ha_state()

    async def async_update(self):
        try:
            src_id = await self._amp.get_source()
            self._attr_current_option = self._reverse_source_map.get(src_id)
        except Exception:
            pass
