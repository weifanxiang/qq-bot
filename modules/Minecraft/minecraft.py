from pathlib import Path
import subprocess
from typing import Dict, Iterable, Literal, Optional, Union
import yaml


class Minecraft:
    class Server:
        path: Path
        name: str
        players: list
        lock_file: Path

        def __init__(self, config: Optional[Union[Iterable, Path]] = None, **kwargs):
            self.path = kwargs["path"]
            self.name = kwargs["name"]
            self.lock_file = self.path / "session.lock"
            if config is not None:
                if isinstance(config, Path):
                    config = yaml.safe_load_all(config.open())

                self.config.load_config(config)

        async def send_command(self, sth: str):
            return subprocess.run(
                [
                    "tmux",
                    "send",
                    "-t",
                    "minecraft_{}".format(self.name),
                    sth,
                    "ENTER",
                ],
                cwd=self.path,
            )

        async def start_server(self) -> bool:
            if self.status:
                return False
            try:
                subprocess.run(
                    [
                        "tmux",
                        "new-window",
                        "-d",
                        "-n",
                        "minecraft_{}".format(self.name),
                        self.config.start_sh.name,
                        "ENTER",
                    ],
                    cwd=self.path.absolute(),
                )
            finally:
                self.lock_file.write_text("running")
                return True

        async def stop_server(self) -> bool:
            if not self.status:
                return False
            try:
                await self.send_command("stop")
            finally:
                self.lock_file.unlink()
                return True

        async def send_message(self, msg: str) -> bool:
            if not self.status:
                return False
            try:
                await self.send_command("say {msg}")
            finally:
                return True

        @property
        def status(self) -> bool:
            return self.lock_file.exists()

        class Config:
            start_sh: Path = Path("./start.sh")
            hardcore: bool = False
            pvp: bool = True
            enable_command_block: bool = False
            difficulty: Literal["hard", "normal", "easy", "peaceful"]

            def load_config(self, config: Iterable):
                pass

        config = Config()

    servers_dir: Path
    servers: Dict[str, Server] = {}

    def __init__(self, config: dict = {"mc_dir": "/opt/minecraft/"}):
        self.servers_dir = Path(config["mc_dir"])
        for i in self.servers_dir.iterdir():
            self.servers.update({i.name: self.Server(name=i.name, path=i)})
