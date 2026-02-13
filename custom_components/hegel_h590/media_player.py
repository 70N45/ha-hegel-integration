import logging
from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerDeviceClass,
    MediaPlayerState,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN
from .hegel_backend import HegelAmp

_LOGGER = logging.getLogger(__name__)

VOLUME_STEP = 5


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        HegelH590Receiver(data["amp"], entry.data["name"], entry.data["host"], data["sources"]),
    ])


class HegelH590Receiver(MediaPlayerEntity):
    """Hegel H590 receiver entity.

    Uses device_class RECEIVER so that HomeKit exposes it as a Receiver
    accessory with native input source selection, volume control, and
    mute — when configured in accessory mode.
    """

    _attr_device_class = MediaPlayerDeviceClass.RECEIVER
    _attr_supported_features = (
        MediaPlayerEntityFeature.TURN_ON
        | MediaPlayerEntityFeature.TURN_OFF
        | MediaPlayerEntityFeature.VOLUME_SET
        | MediaPlayerEntityFeature.VOLUME_STEP
        | MediaPlayerEntityFeature.VOLUME_MUTE
        | MediaPlayerEntityFeature.SELECT_SOURCE
    )

    def __init__(self, amp: HegelAmp, name: str, host: str, sources: dict):
        self._amp = amp
        self._attr_name = name
        self._attr_unique_id = f"hegel_h590_{host}"
        self._source_map = dict(sources)
        self._reverse_source_map = {v: k for k, v in sources.items()}
        self._attr_source_list = list(sources.keys())
        self._state = MediaPlayerState.OFF
        self._volume = 0.0
        self._source = None
        self._muted = False

    @property
    def state(self):
        return self._state

    @property
    def volume_level(self):
        return self._volume

    @property
    def is_volume_muted(self):
        return self._muted

    @property
    def source(self):
        return self._source

    async def async_turn_on(self):
        await self._amp.set_power(True)
        self._state = MediaPlayerState.ON
        self.async_write_ha_state()

    async def async_turn_off(self):
        await self._amp.set_power(False)
        self._state = MediaPlayerState.OFF
        self.async_write_ha_state()

    async def async_set_volume_level(self, volume: float):
        await self._amp.set_volume(int(volume * 100))
        self._volume = volume
        self.async_write_ha_state()

    async def async_volume_up(self):
        new_vol = min(100, int(self._volume * 100) + VOLUME_STEP)
        await self._amp.set_volume(new_vol)
        self._volume = new_vol / 100.0
        self.async_write_ha_state()

    async def async_volume_down(self):
        new_vol = max(0, int(self._volume * 100) - VOLUME_STEP)
        await self._amp.set_volume(new_vol)
        self._volume = new_vol / 100.0
        self.async_write_ha_state()

    async def async_mute_volume(self, mute: bool):
        await self._amp.set_mute(mute)
        self._muted = mute
        self.async_write_ha_state()

    async def async_select_source(self, source: str):
        source_id = self._source_map.get(source)
        if source_id is not None:
            await self._amp.set_source(source_id)
            self._source = source
            self.async_write_ha_state()

    async def async_update(self):
        try:
            power = await self._amp.get_power()
            self._state = MediaPlayerState.ON if power else MediaPlayerState.OFF
            self._volume = await self._amp.get_volume() / 100.0
            self._muted = await self._amp.get_mute()
            src_id = await self._amp.get_source()
            self._source = self._reverse_source_map.get(src_id)
        except Exception:
            pass  # Keep last known state if unreachable
