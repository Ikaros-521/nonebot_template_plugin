from pathlib import Path
from typing import List, Union

from nonebot import on_command
from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupMessageEvent,
    Message,
    MessageSegment,
    PrivateMessageEvent,
)
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.params import CommandArg

from .types import ReplyFileTuple, ReplyTuple
from .utils import get_age_calc_api, get_random_dog_pic

# region matchers
# 试试看，在 vscode 里，# region ... # endregion 注释之间的代码可以折叠

# 获取当前命令型消息的元组形式命令名，简单说就是 触发的命令（不含命令前缀）
# 你测试的时候，可以看下你 env的配置中的命令起始字符 COMMAND_START，根据你的命令前缀加上cmd的命令词即可。
# 例如 COMMAND_START=["/"]  cmd1的触发命令（【】内的是命令啊，别把【】也打进去了）就是 【/本地图片】 或者 【/本地图片别名】
# 需要传参数的命令，例如cmd3的触发命令就是 【/本地图片含传参 图片1】
local_pic = on_command("本地图片", aliases={"本地图片别名"})
# 那么下面这行就是 触发命令为 狗狗图 或者 狗狗图别名 。 其中 aliases是命令的别名，都可以触发。
dogs_pic = on_command("狗狗图", aliases={"狗狗图别名"})
local_pic_with_args = on_command("本地图片含传参")

# 读取本地文件中的内容返回
local_file = on_command("本地文件含传参")

# 固定命令触发，直接返回固定文本
regular_text = on_command("固定文本")
# 固定命令 追加一个传参 触发，直接返回对应的固定文本
regular_text_with_args = on_command("固定文本含传参")

# 调用别人的API时候，要求你传入一个参数这种。然后以回复的形式返回
# 例子：传入 年-月-日 计算生肖
api_zodiac = on_command("生肖计算")

# 图片+文字 合并转发
forward_msg = on_command("合并转发")

# endregion


# 使用 local_pic 响应器的 handle 装饰器装饰了一个函数_
# _函数会被自动转换为 Dependent 对象，并被添加到 local_pic 的事件处理流程中
@local_pic.handle()
# 这里获取一个 Matcher 对象，用于回复消息等
async def _(matcher: Matcher):
    # 文件路径，这里使用 Path 对象
    # 这里的路径是 插件目录/res/104117310_p0.jpg
    file_path = Path(__file__).parent / "res" / "104117310_p0.jpg"

    # 可以是相对路径（./ 开头，相对于运行 nb run 的目录）
    # file_path = Path("./res/104117310_p0.jpg")

    # 可以是绝对路径（Windows 盘符:/ 开头，Linux / 开头）
    # file_path = Path("C:/res/104117310_p0.jpg")  # Windows
    # file_path = Path("/home/res/104117310_p0.jpg")  # Linux

    try:
        # 使用MessageSegment.image方法创建一个消息段，该消息段包含了文件路径对应的图像文件，并将其赋值给变量msg。
        # 在这个过程中，代码通过file参数将文件路径传递给image方法，以指定要发送的图像文件
        # file支持很多类型 Union[str, bytes, BytesIO, Path]，可以看看源码
        msg = MessageSegment.image(file=file_path)
    except Exception:
        # 打印错误详细信息
        logger.exception("发送失败")
        msg = "\n发送失败喵，请检查后台日志排查问题~"

    # 返回msg信息 结束，并且@触发命令的人（at_sender=True），不需要@可以改为False或者删掉
    await matcher.finish(msg, at_sender=True)


@dogs_pic.handle()
# 获取命令型消息命令后跟随的参数 CommandArg 获取命令后传入的参数，解析处理
async def _(matcher: Matcher, arg: Message = CommandArg()):
    # 调用了 msg 对象的 extract_plain_text 方法，该方法用于从消息对象中提取纯文本内容
    # 它会自动去除消息中的所有格式和特殊字符，只返回包含文本的部分
    # 接着，strip 方法被用于去除返回的字符串的首尾空格
    content = arg.extract_plain_text().strip()
    # 打印日志 传参内容 content，可以看看
    logger.info(content)

    # 等待请求函数返回我们需要的结果
    pic = await get_random_dog_pic()
    # 返回的 pic 如果是 None 的话 就是请求中出问题了
    if not pic:
        # 调用了 NoneBot Matcher 中的 finish 方法，该方法用于结束一个会话，并发送一条消息（可选）
        await matcher.finish("请求失败，这里写相关的错误的提示内容，告诉用户失败了")

    # 调用了 NoneBot Matcher 中的 finish 方法，该方法用于结束一个会话，并发送一个消息作为会话的最终结果
    # finish 里面调用了 MessageSegment 对象的 image 方法，该方法用于构造一个图片消息段。
    # file 参数指定了图片数据，该图片将被发送给机器人用户。
    # await 关键字用于调用异步方法
    await matcher.finish(MessageSegment.image(file=pic))


@local_pic_with_args.handle()
async def _(matcher: Matcher, arg: Message = CommandArg()):
    content = arg.extract_plain_text().strip()
    logger.info(content)

    # 存储 传参关键词 和 返回的内容
    # 可以使用相对和绝对路径，可以看看上面
    #
    # 这里的 `变量名: 类型` 是类型注解，让编辑器知道这里的变量是什么类型的
    # 提示：在 vscode 中 Ctrl+点击 可以跳转定义
    pic_path = Path(__file__).parent / "res" / "pic"
    data: List[ReplyFileTuple] = [
        ReplyFileTuple("图片1", pic_path / "77470708_p5.png"),
        ReplyFileTuple("图片2", pic_path / "81274446_p0.jpg"),
        ReplyFileTuple("图片3", pic_path / "104117310_p0.jpg"),
    ]

    # 循环遍历 data 数据源中的所有数据项
    for kw, file in data:
        # 查找与用户输入的传参关键词 content 匹配的数据项 item["keyword"]
        if content == kw:
            # 使用 MessageSegment.image 方法创建一个消息段，该消息段包含了文件路径对应的图像文件，并将其赋值给变量 msg。
            # 在这个过程中，代码通过 file 参数将文件路径传递给 image 方法，以指定要发送的图像文件
            # file支持很多类型 Union[str, bytes, BytesIO, Path]，可以看看源码
            msg = MessageSegment.image(file)
            # 退出循环
            break

    else:
        # 如果循环没有被中断，即所有的数据项都被遍历完，就执行这个语句块
        # msg 为 字符串信息
        msg = "\n果咩，没有此关键词的索引，请联系bot管理员添加~"

    # 返回 msg 信息并结束，并且@触发命令的人（at_sender=True），不需要@可以删掉
    await matcher.finish(msg, at_sender=True)


@local_file.handle()
async def _(matcher: Matcher, arg: Message = CommandArg()):
    content = arg.extract_plain_text().strip()
    # 打印日志 传参内容content，可以看看
    logger.info(content)

    txt_path = Path(__file__).parent / "res" / "txt"
    data: List[ReplyFileTuple] = [
        ReplyFileTuple("文件1", txt_path / "1.txt"),
        ReplyFileTuple("文件2", txt_path / "2.txt"),
        ReplyFileTuple("文件3", txt_path / "3.txt"),
    ]

    # 循环遍历 data 数据源中的所有数据项
    for kw, file in data:
        if content == kw:
            try:
                # 使用 Path.read_text() 来读取文件内容。如果文件很大，建议使用异步读取文件（自行搜索）
                # 使用 Message 构建消息对象，会解析文本内 CQ 码
                msg = Message(file.read_text())
                break
            except Exception:
                # 输出错误消息并给出回复
                logger.exception("读取文件失败")
                msg = "\n读取文件失败了，请查看后台输出"

    else:
        # 如果循环没有被中断，即所有的数据项都被遍历完，就执行这个语句块
        # msg 为 字符串信息
        msg = "\n果咩，没有此关键词的索引，请联系bot管理员添加~"

    # 返回 msg 信息并结束，并且@触发命令的人（at_sender=True），不需要@可以删掉
    await matcher.finish(msg, at_sender=True)


@regular_text.handle()
async def _(matcher: Matcher):
    # 文本赋值给msg
    msg = "这是一个固定的句子，自行编辑即可。"
    # 返回 msg 信息并结束，并且@触发命令的人（at_sender=True），不需要@可以删掉
    await matcher.finish(msg, at_sender=True)


@regular_text_with_args.handle()
async def _(matcher: Matcher, arg: Message = CommandArg()):
    content = arg.extract_plain_text().strip()
    # 打印日志 传参内容content，可以看看
    logger.info(content)

    # 存储 传参关键词 和 返回的内容
    data = [
        ReplyTuple("关键词1", "这是一个普通的句子，123abc@#$"),
        ReplyTuple("关键词2", "链接：www.baidu.com"),
        ReplyTuple(
            "关键词3",
            "随机发病语录：https://github.com/Ikaros-521/nonebot_plugin_random_stereotypes",
        ),
    ]

    # 循环遍历 data 数据源中的所有数据项
    for kw, msg in data:
        # 查找与用户输入的传参关键词content 匹配的数据项 item["keyword"]
        if content == kw:
            # msg = msg
            # 退出循环
            break

    else:
        # 如果循环没有被中断，即所有的数据项都被遍历完，就执行这个语句块
        # msg 为 字符串信息
        msg = "\n果咩，没有此关键词的索引，请联系bot管理员添加~"

    # 返回 msg 信息并结束，并且@触发命令的人（at_sender=True），不需要@可以删掉
    await matcher.finish(msg, at_sender=True)


@api_zodiac.handle()
async def _(matcher: Matcher, arg: Message = CommandArg()):
    content = arg.extract_plain_text().strip()

    # 调用 API 获取返回的文本赋值给 msg
    res = await get_age_calc_api(content)

    if res is None:
        # 返回的 msg 如果是 None 的话 就是请求中出问题了
        await matcher.finish(
            "\n请求异常，可能是网络问题或者API挂了喵~（请检查后台日志排查）",
            at_sender=True,
        )

        # 这里由于调用了 Matcher.finish()，函数会抛出 FinishedException，之后就不会向下执行了，所以不需要写 else
        # Tip: 所有返回值为 NoReturn 的函数调用的时候都会抛出错误或者为死循环

    # 我们把提示语追加到返回的字符串句前，方便用户理解
    # 回复用户消息
    await matcher.finish(f"返回结果：{res}", reply_message=True)


@forward_msg.handle()
# 这里获取了事件所属的 Bot，和对应 MessageEvent（消息事件）
async def _(
    bot: Bot,
    event: Union[GroupMessageEvent, PrivateMessageEvent],
    matcher: Matcher,
):
    # 判断消息来源（群聊 / 私聊）
    is_group = isinstance(event, GroupMessageEvent)

    # 图片路径
    img_path = Path(__file__).parent / "res" / "pic" / "77470708_p5.png"

    # 随便定义了个字符串数组 存两数据演示一下。可以将具体需要发送的文本信息存放到该数组中
    out_str_arr = ["数组中的字符串1", "数组中的字符串2"]

    # 定义了一个空的 msgList 列表
    msgList = []

    # 转发者的昵称
    # 这里使用消息发送人的 群名片 或 昵称 或 “亻尔女子”，当前值 if 判断为假时自动向后取值
    nickname = event.sender.card or event.sender.nickname or "亻尔女子"

    # 遍历 out_str_arr 数组
    for out_str in out_str_arr:
        # 将多个元素添加到列表 msgList 中
        #
        # list.extend() 方法可以接受一个可迭代对象（Iterator）作为参数，如列表、元组或集合等。
        # 当该方法被调用时，它将可迭代对象中的所有元素添加到 msgList 列表中。
        msgList.extend(
            [
                # 创建一些自定义的节点，供消息链使用
                MessageSegment.node_custom(
                    user_id=event.user_id,  # 转发者的QQ号（这里使用消息发送人 qq）
                    nickname=nickname,
                    content=Message(MessageSegment.text(out_str)),
                ),
                MessageSegment.node_custom(
                    user_id=event.user_id,
                    nickname=nickname,
                    content=Message(MessageSegment.image(file=img_path)),
                ),
            ]
        )

    # 异常捕获
    try:
        # 针对不同的消息来源（群聊或私聊），程序选择调用不同的函数进行消息发送。如果出现异常，则抛出错误提示消息，以便修复问题。
        if is_group:
            # 构建群聊合并转发消息。
            # 具体来说，该方法会将 msgList 列表中的信息发送到指定的 group_id 群组中。
            # 其中，group_id 表示目标群组的 ID，messages 表示需要发送的消息列表
            await bot.send_group_forward_msg(group_id=event.group_id, messages=msgList)
        else:
            # 构建私聊合并转发消息。
            # 将 msgList 列表中的信息发送到指定的 user_id 用户中。
            # 其中，user_id 表示目标用户的 ID，messages 表示需要发送的消息列表
            await bot.send_private_forward_msg(user_id=event.user_id, messages=msgList)

    except Exception:
        logger.exception("消息发送失败")
        msg = "果咩，数据发送失败喵~请查看源码和日志定位问题原因"
        await matcher.finish(msg, reply_message=True)
