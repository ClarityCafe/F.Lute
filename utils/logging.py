from logging import getLogger, INFO, DEBUG, basicConfig

basicConfig(level=INFO)
log = getLogger("MusicBot")


def info(msg: str):
    log.info(msg)


def warn(msg: str):
    log.warn(msg)


def debug(msg: str):
    log.debug(msg)


def error(msg: str):
    log.error(msg)
