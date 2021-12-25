from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from loguru import logger
from pathlib import Path
from graia.ariadne.message.element import Plain
from graia.ariadne.model import Group, Member
from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.element import Plain, At
from typing import Dict, Literal
import subprocess

saya = Saya.current()
channel = Channel.current()
channel.name(__name__)


class Minecraft:
    class Server:
        path: Path
        name: str
        players: list
        lock_file: Path

        def __init__(self, **kwargs):
            self.path = kwargs["path"]
            self.name = kwargs["name"]
            self.lock_file = self.path / "session.lock"

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
                print("{self.name}")
                subprocess.run(
                    [
                        "tmux",
                        "new",
                        "-s",
                        "-d",
                        "minecraft_{}".format(self.name),
                        "./start.sh",
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

            async def load_config(self):
                pass

    servers_dir: Path
    servers: Dict[str, Server] = {}

    def __init__(self, config: dict = {"mc_dir": "/root/minecraft/"}):
        self.servers_dir = Path(config["mc_dir"])
        for i in self.servers_dir.iterdir():
            self.servers.update({i.name: self.Server(name=i.name, path=i)})


minecraft = Minecraft()


@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def event_receiver(
    app: Ariadne, message: MessageChain, group: Group, sender: Member
):
    if message.asDisplay().startswith("#mc "):
        await app.sendMessage(
            group,
            MessageChain.create(
                [
                    At(sender.id),
                    Plain(await judge(message.asDisplay()[4:].strip())),
                ]
            ),
        )


async def judge(message: str) -> str:
    if message.startswith("start"):
        return "已开启" if await minecraft.servers[message[6:]].start_server() else "启动失败"
    elif message.startswith("stop"):
        return "已关闭" if await minecraft.servers[message[5:]].stop_server() else "关闭失败"
    elif message.startswith("status"):
        return "该服务器开启状态为:" + str(minecraft.servers[message[7:]].status)
    elif message.startswith("say"):
        command_list = message[4:].split()
        return (
            "已发送"
            if await minecraft.servers[command_list[0]].send_message(command_list[1])
            else "Error."
        )
    else:
        return "服务器暂时不支持这个命令"
