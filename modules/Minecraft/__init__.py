from graia.broadcast.exceptions import ExecutionStop
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from loguru import logger
from minecraft import Minecraft

from graia.ariadne.message.element import Plain
from graia.ariadne.model import Group, Member
from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.element import Plain, At
from graia.broadcast.builtin.decorators import Depend
from arclet.alconna.component import Option, Subcommand
from arclet.alconna.types import AnyStr
from graia.ariadne.message.parser.alconna import (
    AlconnaDispatcher,
    Alconna,
    Arpamar,
)


def require_group(*group_id: int):
    async def wrapper(group: Group):
        if group.id not in group_id:
            raise ExecutionStop

    return wrapper


saya = Saya.current()
channel = Channel.current()
channel.name(__name__)


minecraft = Minecraft()


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage], decorators=[Depend(require_group(703208283))]
    )
)
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
