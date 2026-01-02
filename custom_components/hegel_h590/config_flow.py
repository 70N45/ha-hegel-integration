import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers import selector

from .const import DOMAIN, DEFAULT_PORT, DEFAULT_NAME, ALL_SOURCES


DEVICE_CLASSES = ["media_player", "receiver"]


class HegelH590ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(
                title=user_input["name"],
                data=user_input,
            )

        schema = vol.Schema(
            {
                vol.Required("name", default=DEFAULT_NAME): str,
                vol.Required("host"): str,
                vol.Required("port", default=DEFAULT_PORT): int,
                vol.Required(
                    "sources",
                    default=["Heimkino", "Phono", "USB", "Network"],
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=list(ALL_SOURCES.keys()),
                        multiple=True,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Required(
                    "device_class", default="media_player"
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=DEVICE_CLASSES,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )


        return self.async_show_form(
            step_id="user",
            data_schema=schema,
        )
