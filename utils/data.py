import os


def resolve_data_path(path: str, makedirs_if_not_exists=True) -> str:
    """
    解析路径：
    - 如果是绝对路径，则直接返回。
    - 如果是相对路径，则返回 ../data/{path}，基于当前 py 文件所在目录。
    :param  path: 路径
    :param  makedirs_if_not_exists: 如果路径不存在，是否创建
    """
    if not os.path.isabs(path):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(current_dir, '..', 'data', path)
    if makedirs_if_not_exists and not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
    return os.path.abspath(path)
