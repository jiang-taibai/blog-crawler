import random


def generate_random_string(length=8):
    """
    生成指定长度的随机字符串
    :param length: 随机字符串长度
    :return: 随机字符串
    """
    # 生成一个随机小数
    random_float = random.random()
    # 将小数转为十六进制字符串，去掉 "0x" 前缀
    random_hex = hex(int(random_float * (16 ** length)))[2:]
    # 返回生成的随机字符串，确保它是指定长度
    return random_hex[:length]
