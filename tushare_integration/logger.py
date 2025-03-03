import logging


def _disable_httpx_logger() -> None:
    """
    禁用 httpx 的日志输出，将其日志级别设置为 WARNING
    """
    httpx_logger = logging.getLogger("httpx")
    httpx_logger.setLevel(logging.WARNING)


def get_level(level: str) -> int:
    """获取日志级别

    Args:
        level: 日志级别名称

    Returns:
        int: 日志级别
    """
    return getattr(logging, level.upper(), logging.INFO)


def init_logger(level: int = logging.INFO) -> None:
    """初始化日志配置

    Args:
        level: 日志级别，默认为 INFO
    """
    # 禁用 httpx 日志
    _disable_httpx_logger()

    # 创建根日志记录器
    logger = logging.getLogger('tushare_integration')

    # 阻止日志传递给父记录器
    logger.propagate = False

    # 设置日志级别
    logger.setLevel(level)
    # 同时设置根日志记录器的级别
    logging.getLogger().setLevel(level)

    # 如果已经有处理器，不重复添加
    if logger.handlers:
        # 更新现有处理器的日志级别
        for handler in logger.handlers:
            handler.setLevel(level)
        return

    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

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
