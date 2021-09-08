# coding:utf-8
import os
import re

from win32com.shell import shell, shellcon


def checkDirExists(dirPath: str):
    """ 检查文件夹是否存在装饰器 """

    def outer(fun):
        def inner(*args, **kwargs):
            os.makedirs(dirPath, exist_ok=True)
            return fun(*args, **kwargs)
        return inner

    return outer


def moveToTrash(path: str):
    """ 将文件移动到回收站 """
    shell.SHFileOperation((0, shellcon.FO_DELETE, path, None, shellcon.FOF_SILENT |
                           shellcon.FOF_ALLOWUNDO | shellcon.FOF_NOCONFIRMATION, None, None))


def adjustName(name: str):
    """ 调整文件名

    Returns
    -------
    name: str
        调整后的名字
    """
    rex = r'[><:\\/\*\?]'
    name = re.sub(r'[\"]', "'", name)
    name = name.strip()

    if re.search(rex, name):
        # 替换不符合命名规则的专辑名
        name = re.sub(rex, ' ', name)
        name = re.sub(r'[\"]', "'", name)
        name = name.strip()

    return name


def getCoverPath(name: str, coverType: str) -> str:
    """ 获取封面路径

    Parameters
    ----------
    name: str
        封面名字，格式为 `singer_modifiedAlbum`

    coverType: str
        封面类型，有以下几种：
        * `album_big` - 大默认专辑封面
        * `album_small` - 小默认专辑封面
        * `playlist_big` - 大默认播放列表封面
        * `playlist_small` - 小默认播放列表封面
    """
    cover_path_dict = {
        "album_big": ":/images/default_covers/album_200_200.png",
        "album_small": ":/images/default_covers/album_113_113.png",
        "playlist_big": ":/images/default_covers/playlist_275_275.png",
        "playlist_small": ":/images/default_covers/playlist_135_135.png",
    }
    if coverType not in cover_path_dict:
        raise ValueError(f"{coverType} 非法")

    coverPath = cover_path_dict[coverType]
    coverFolder = f"Album_Cover/{name}"
    pic_list = os.listdir(coverFolder) if os.path.exists(coverFolder) else []
    # 如果目录下有封面就用这个封面作为albumCard的背景
    if pic_list and os.path.isfile(os.path.join(coverFolder, pic_list[0])):
        coverPath = os.path.join(coverFolder, pic_list[0])

    return coverPath