import logging
from homeassistant.components.media_player import (
    MediaPlayerEntity, MediaPlayerEntityFeature, MediaPlayerState
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import ALL_SOURCES
from .hegel_backend import HegelAmp

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    amp = HegelAmp(entry.data["host"], entry.data["port"])
    selected_sources = {name: ALL_SOURCES[name] for name in entry.data["sources"]}

    async_add_entities([
        HegelH590MediaPlayer(amp, entry.data["name"], selected_sources),
        HegelH590Speaker(amp, entry.data["name"], selected_sources)
    ])

class HegelH590MediaPlayer(MediaPlayerEntity):
    """Main HA entity for dashboards/automations."""

    def __init__(self, amp: HegelAmp, name, sources):
        self._amp = amp
        self._attr_name = name
        self._source_map = {name: id for name, id in sources.items()}
        self._enabled_sources = list(sources.keys())
        self._attr_unique_id = f"{name}_{amp._host}_main"
        self._attr_supported_features = (
            MediaPlayerEntityFeature.TURN_ON
            | MediaPlayerEntityFeature.TURN_OFF
            | MediaPlayerEntityFeature.VOLUME_SET
            | MediaPlayerEntityFeature.SELECT_SOURCE
        )
        self._state = MediaPlayerState.OFF
        self._volume = 0.0
        self._source = None

    async def async_turn_on(self):
        await self._amp.set_power(True)
        self._state = MediaPlayerState.ON
        self.async_write_ha_state()

    async def async_turn_off(self):
        await self._amp.set_power(False)
        self._state = MediaPlayerState.OFF
        self.async_write_ha_state()

    async def async_set_volume_level(self, volume):
        await self._amp.set_volume(int(volume * 100))
        self._volume = volume
        self.async_write_ha_state()

    async def async_select_source(self, source):
        source_id = self._source_map[source]
        await self._amp.set_source(source_id)
        self._source = source
        self.async_write_ha_state()

    async def async_update(self):
        try:
            self._state = MediaPlayerState.ON if await self._amp.get_power() else MediaPlayerState.OFF
            self._volume = await self._amp.get_volume() / 100.0
            src_id = await self._amp.get_source()
            self._source = None
            for name, id in self._source_map.items():
                if id == src_id:
                    self._source = name
        except Exception:
            pass  # Keep last known state if unreachable

class HegelH590Speaker(MediaPlayerEntity):
    """HomeKit-friendly entity exposing power, volume, and inputs."""

    def __init__(self, amp: HegelAmp, name, sources):
        self._amp = amp
        self._attr_name = f"{name} Speaker"
        self._source_map = {name: id for name, id in sources.items()}
        self._enabled_sources = list(sources.keys())
        self._attr_unique_id = f"{self._attr_name}_{amp._host}"
        self._attr_supported_features = (
            MediaPlayerEntityFeature.TURN_ON
            | MediaPlayerEntityFeature.TURN_OFF
            | MediaPlayerEntityFeature.VOLUME_SET
            | MediaPlayerEntityFeature.SELECT_SOURCE
        )
        self._state = MediaPlayerState.OFF
        self._volume = 0.0
        self._source = None

    async def async_turn_on(self):
        await self._amp.set_power(True)
        self._state = MediaPlayerState.ON
        self.async_write_ha_state()

    async def async_turn_off(self):
        await self._amp.set_power(False)
        self._state = MediaPlayerState.OFF
        self.async_write_ha_state()

    async def async_set_volume_level(self, volume):
        await self._amp.set_volume(int(volume * 100))
        self._volume = volume
        self.async_write_ha_state()

    async def async_select_source(self, source):
        source_id = self._source_map[source]
        await self._amp.set_source(source_id)
        self._source = source
        self.async_write_ha_state()

    async def async_update(self):
        try:
            self._state = MediaPlayerState.ON if await self._amp.get_power() else MediaPlayerState.OFF
            self._volume = await self._amp.get_volume() / 100.0
            src_id = await self._amp.get_source()
            self._source = None
            for name, id in self._source_map.items():
                if id == src_id:
                    self._source = name
        except Exception:
            pass
