import logging

LOGGER = logging.getLogger()
DATE_FMT = "%Y-%m-%d %H:%M:%S"
MSG_FMT = "[{asctime}] [{levelname}] {name}: {message}"


# TODO: use dictconfig to setup loggers


def setup_file_logger(level: str = 'INFO', out_file: str = 'output.log'):
    level = getattr(logging, level.upper()) 
    file_handler = logging.FileHandler(filename=out_file, encoding="utf-8", mode="w")

    logger_fmt = logging.Formatter(fmt=MSG_FMT, datefmt=DATE_FMT, style="{")
    file_handler.setFormatter(logger_fmt)

    LOGGER.addHandler(file_handler)
    LOGGER.setLevel(level) 
    
    return logging.getLogger('file_handler')

def setup_stream_logger(level: str = 'INFO'):
    level = getattr(logging, level.upper()) 
    stream_handler = logging.StreamHandler()

    logger_fmt = logging.Formatter(fmt=MSG_FMT, datefmt=DATE_FMT, style="{")
    stream_handler.setFormatter(logger_fmt)
    
    LOGGER.addHandler(stream_handler)
    LOGGER.setLevel(level) 
    
    return logging.getLogger('stream_handler')

