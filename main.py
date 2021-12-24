import os
from graia.saya import Saya
from graia.saya.builtins.broadcast import BroadcastBehaviour
import asyncio

from graia.broadcast import Broadcast

from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain
from graia.ariadne.model import Friend, MiraiSession

loop = asyncio.new_event_loop()

bcc = Broadcast(loop=loop)
saya = Saya(bcc)
saya.install_behaviours(BroadcastBehaviour(bcc))
app = Ariadne(
    broadcast=bcc,
    connect_info=MiraiSession(
        host="http://localhost:8080",  # 填入 HTTP API 服务运行的地址
        verify_key="graia-mirai-api-http-authkey",  # 填入 verifyKey
        account=2324523071,  # 你的机器人的 qq 号
    ),
)


with saya.module_context():
    saya.require("modules.minecraft")

# @bcc.receiver("FriendMessage")
# async def friend_message_listener(app: Ariadne, friend: Friend):
#     await app.sendMessage(friend, MessageChain.create([Plain("Hello, World!")]))
#     # 实际上 MessageChain.create(...) 有没有 "[]" 都没关系

loop.run_until_complete(app.lifecycle())
