import json
from typing import Any, Literal, NoReturn, Union, overload

from aiohttp import ClientSession
from nonebot.log import logger

from .types import DogApiReturn

# region async_request


# 下面这些是该方法的重载，用于类型提示
@overload
async def async_request(
    url: str,
    is_raw: Literal[False] = False,
    is_json: Literal[False] = False,
    **kwargs,
) -> Union[str, None]:
    ...


@overload
async def async_request(
    url: str,
    is_raw: Literal[True] = True,
    is_json: Literal[False] = False,
    **kwargs,
) -> Union[bytes, None]:
    ...


@overload
async def async_request(
    url: str,
    is_raw: Literal[False] = False,
    is_json: Literal[True] = True,
    **kwargs,
) -> Union[Any, None]:
    ...


@overload
async def async_request(
    url: str,
    is_raw: Literal[True] = True,
    is_json: Literal[True] = True,
    **kwargs,
) -> NoReturn:
    ...


async def async_request(
    url: str,
    is_raw: bool = False,
    is_json: bool = False,
    **kwargs,
):
    """
    异步请求 URL

    Args:
        url: 要请求的 URL
        is_raw: 是否返回 bytes 类型的值
        is_json: 将 json 格式的返回值解析为 dict

    Returns:
        请求 & 解析结果
    """

    # 不许同时传两个
    if is_raw and is_json:
        raise ValueError("不能同时传入 `raw` 与 `json`")

    # 捕获可能出现的异常
    try:
        # 创建一个 aiohttp.ClientSession 对象，该对象可以管理 HTTP 连接和请求。
        # 使用 async with 语句可以确保在请求完成后正确关闭连接。
        async with ClientSession() as s:
            # 使用 ClientSession 对象的 get 方法发送 HTTP GET 请求。url 参数指定请求的 URL。
            # 使用 async with 语句可以确保请求完成后正确关闭响应对象。
            async with s.get(url, **kwargs) as r:
                if is_raw:
                    # 返回 bytes
                    return await r.read()

                # 将 res 读为文本，会自动检测编码
                res = await r.text()
                if is_json:
                    # 将请求结果作为 json 解析为 dict，返回
                    return json.loads(res)

                return res

    except Exception:
        # 出错打印错误日志并返回 None
        logger.exception("请求出错")
        return None


# endregion


async def get_age_calc_api(birthday: str) -> Union[str, None]:
    """
    调用生肖计算 API

    Args:
        birthday: 生日

    Returns:
        调用结果
    """
    return await async_request(
        "https://zj.v.api.aa1.cn/api/Age-calculation/",
        params={"birthday": birthday},
    )


async def get_random_dog_pic() -> Union[bytes, None]:
    """
    调用随机狗狗图 API

    Returns:
        随机狗狗图
    """
    # 请求 API 并使用 pydantic 解析返回值（提示：在 vscode 中 Ctrl+点击 可以跳转定义）
    res = DogApiReturn(
        **(
            await async_request(  # type: ignore
                "https://dog.ceo/api/breeds/image/random",
                is_json=True,
            )
        )
    )

    # 如果返回值正常，就请求返回的图片 URL 并返回图片数据
    if res and res.status == "success":
        img_url = res.message
        return await async_request(img_url, is_raw=True)
