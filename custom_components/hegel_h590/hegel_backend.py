# hegel_backend.py
import socket
import asyncio
import logging

_LOGGER = logging.getLogger(__name__)

class HegelAmp:
    def __init__(self, host, port):
        self._host = host
        self._port = port

    async def send_command(self, command: str) -> str:
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

    async def get_power(self):
        resp = await self.send_command("-p.?")
        return resp.endswith(".1")

    async def set_power(self, on: bool):
        await self.send_command(f"-p.{int(on)}")

    async def get_volume(self):
        resp = await self.send_command("-v.?")
        return int(resp.split(".")[1])

    async def set_volume(self, volume: int):
        await self.send_command(f"-v.{volume}")

    async def get_source(self):
        resp = await self.send_command("-i.?")
        return int(resp.split(".")[1])

    async def set_source(self, source_id: int):
        await self.send_command(f"-i.{source_id}")

    async def get_mute(self):
        resp = await self.send_command("-m.?")
        return resp.endswith(".1")

    async def set_mute(self, mute: bool):
        await self.send_command(f"-m.{int(mute)}")
