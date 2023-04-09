from pathlib import Path
from typing import NamedTuple

from nonebot.internal.adapter import Message, MessageSegment
from pydantic import BaseModel


# pydantic.BaseModel 可以解析并验证数据，详细用法可以去搜索一下
class DogApiReturn(BaseModel):
    message: str
    status: str


# NamedTuple 用于给 tuple 内的元素定义名称，便于编辑器的代码提示
class ReplyTuple(NamedTuple):
    keyword: str
    msg: Message | MessageSegment | str


class ReplyFileTuple(NamedTuple):
    keyword: str
    file: Path
