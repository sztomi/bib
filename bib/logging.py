import logging


def get_logger(name) -> logging.RootLogger:
  logger = logging.getLogger(name)
  logger.setLevel(logging.DEBUG)
  ch = logging.StreamHandler()
  #ch.setLevel(logging.DEBUG)
  formatter = logging.Formatter('{asctime}   {name:24} {levelname:8} - {message}', style="{")
  ch.setFormatter(formatter)
  logger.addHandler(ch)
  return logger