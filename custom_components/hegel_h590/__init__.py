from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import (
    DOMAIN, ALL_SOURCES,
    MODE_RECEIVER, MODE_RECEIVER_FAN, MODE_FAN_ONLY, MODE_WORKAROUND, MODE_BOTH,
)
from .hegel_backend import HegelAmp


def _platforms_for_mode(mode: str) -> list[str]:
    if mode == MODE_RECEIVER:
        return ["media_player"]
    if mode == MODE_RECEIVER_FAN:
        return ["media_player", "fan"]
    if mode == MODE_FAN_ONLY:
        return ["fan"]
    if mode == MODE_WORKAROUND:
        return ["fan", "select", "switch"]
    # MODE_BOTH
    return ["media_player", "fan", "select", "switch"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    amp = HegelAmp(entry.data["host"], entry.data["port"])
    selected_sources = {name: ALL_SOURCES[name] for name in entry.data["sources"]}

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "amp": amp,
        "sources": selected_sources,
    }

    mode = entry.data.get("mode", MODE_RECEIVER)
    platforms = _platforms_for_mode(mode)
    await hass.config_entries.async_forward_entry_setups(entry, platforms)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    mode = entry.data.get("mode", MODE_RECEIVER)
    platforms = _platforms_for_mode(mode)
    ok = await hass.config_entries.async_unload_platforms(entry, platforms)
    if ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return ok
