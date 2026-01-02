import asyncio
import socket
import logging
from homeassistant.components.media_player import MediaPlayerEntity
from homeassistant.components.media_player.const import (
    MediaPlayerEntityFeature, MediaPlayerState
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import ALL_SOURCES

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    async_add_entities([HegelH590MediaPlayer(entry)])

class HegelH590MediaPlayer(MediaPlayerEntity):
    def __init__(self, entry: ConfigEntry):
        self._host = entry.data["host"]
        self._port = entry.data["port"]
        self._attr_name = entry.data["name"]

        self._enabled_sources = entry.data["sources"]
        self._source_map = {name: ALL_SOURCES[name] for name in self._enabled_sources}

        # Always media_player for HomeKit compatibility
        self._device_type = "media_player"

        self._attr_unique_id = f"{self._host}_{self._port}_hegel_h590"

        self._state = MediaPlayerState.OFF
        self._volume = 0.0
        self._muted = False
        self._source = None

        self._attr_supported_features = (
            MediaPlayerEntityFeature.TURN_ON
            | MediaPlayerEntityFeature.TURN_OFF
            | MediaPlayerEntityFeature.VOLUME_SET
            | MediaPlayerEntityFeature.SELECT_SOURCE
        )

    #
    # --- TCP communication ---
    #
    async def _send_command(self, command: str) -> str:
        if not command.endswith("\r"):
            command += "\r"

        def _blocking_call():
            try:
                with socket.create_connection((self._host, self._port), timeout=5) as sock:
                    sock.sendall(command.encode("ascii"))
                    return sock.recv(1024).decode("ascii", errors="ignore").strip()
            except Exception as e:
                _LOGGER.error("Hegel H590 TCP error: %s", e)
                raise

        return await asyncio.to_thread(_blocking_call)

    #
    # --- HA properties ---
    #
    @property
    def state(self):
        return self._state

    @property
    def volume_level(self):
        return self._volume

    @property
    def source(self):
        return self._source

    @property
    def source_list(self):
        return list(self._source_map.keys())

    #
    # --- Controls ---
    #
    async def async_turn_on(self):
        await self._send_command("-p.1")
        self._state = MediaPlayerState.ON
        self.async_write_ha_state()

    async def async_turn_off(self):
        await self._send_command("-p.0")
        self._state = MediaPlayerState.OFF
        self.async_write_ha_state()

    async def async_set_volume_level(self, volume):
        amp_volume = int(volume * 100)
        await self._send_command(f"-v.{amp_volume}")
        self._volume = volume
        self.async_write_ha_state()

    async def async_select_source(self, source):
        source_id = self._source_map[source]
        await self._send_command(f"-i.{source_id}")
        self._source = source
        self.async_write_ha_state()

    #
    # --- Polling ---
    #
    async def async_update(self):
        try:
            power = await self._send_command("-p.?")
            self._state = MediaPlayerState.ON if power.endswith(".1") else MediaPlayerState.OFF

            vol = await self._send_command("-v.?")
            self._volume = int(vol.split(".")[1]) / 100.0

            src = await self._send_command("-i.?")
            src_id = int(src.split(".")[1])
            self._source = None
            for name, sid in self._source_map.items():
                if sid == src_id:
                    self._source = name
                    break
        except Exception:
            # Keep last known state if unreachable
            pass
