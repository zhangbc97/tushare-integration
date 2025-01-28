import logging
from typing import Optional


def init_logger(level: Optional[int] = None) -> None:
    """初始化日志配置

    Args:
        level: 日志级别，默认为 INFO
    """
    # 创建根日志记录器
    logger = logging.getLogger('tushare_integration')

    # 阻止日志传递给父记录器
    logger.propagate = False

    if level is not None:
        logger.setLevel(level)
    else:
        logger.setLevel(logging.INFO)

    # 如果已经有处理器，不重复添加
    if logger.handlers:
        return

    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # 设置日志格式
    formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    console_handler.setFormatter(formatter)

    # 添加处理器到日志记录器
    logger.addHandler(console_handler)


def get_logger() -> logging.Logger:
    """获取日志记录器

    Returns:
        logging.Logger: 日志记录器实例
    """
    return logging.getLogger('tushare_integration')
