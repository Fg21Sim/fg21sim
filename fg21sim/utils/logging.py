# Copyright (c) 2016 Weitian LI <liweitianux@live.com>
# MIT license

"""
Logging utilities.
"""

import sys
import logging
from logging import FileHandler, StreamHandler


def setup_logging(dict_config=None, level=None, stream=None, logfile=None):
    """Setup the logging.
    This will override the logging configurations in the config file
    if specified (e.g., by command line arguments).

    Parameters
    ----------
    dict_config : dict
        Dict of logging configurations specified in the config file.
        If this parameter specified, the logging will be reconfigured.
    level : string;
        Override the existing log level
    stream : string; "stderr", "stdout", or ""
        This controls where the log messages go to.
        If not None, then override the old ``StreamHandler`` settings;
        if ``stream=""``, then disable the ``StreamHandler``.
    logfile : string
        Specify the file where the log messages go to.
        If ``logfile=""``, then disable the ``FileHandler``.

    NOTE
    ----
    If the logging already has ``StreamHandler`` or ``FileHandler``
    configured, then the old handler will be *replaced* (i.e., remove
    the old one, then add the new one).
    """
    # default file open mode for logging to file
    filemode = "a"
    root_logger = logging.getLogger()
    #
    if dict_config:
        # XXX:
        # "basicConfig()" does NOT accept paramter "filemode" if the
        # corresponding parameter "filename" NOT specified.
        filemode = dict_config.pop("filemode", filemode)
        # Clear existing handlers, otherwise further "basicConfig" calls
        # will be ignored
        for handler in root_logger.handlers:
            root_logger.removeHandler(handler)
        # Initialize/reconfigure the logging, which will automatically
        # create a ``Formatter`` for handlers if necessary, and adding
        # the handlers to the "root" logger.
        logging.basicConfig(**dict_config)
    #
    if level is not None:
        level_int = getattr(logging, level.upper(), None)
        if not isinstance(level_int, int):
            raise ValueError("invalid log level: %s" % level)
        root_logger.setLevel(level_int)
    #
    if stream is None:
        pass
    elif stream in ["", "stderr", "stdout"]:
        for handler in root_logger.handlers:
            if isinstance(handler, StreamHandler):
                # remove old ``StreamHandler``
                root_logger.removeHandler(handler)
        if stream == "":
            # disable ``StreamHandler``
            pass
        else:
            # add new ``StreamHandler``
            handler = StreamHandler(getattr(sys, stream))
            root_logger.addHandler(handler)
    else:
        raise ValueError("invalid stream: %s" % stream)
    #
    if logfile is not None:
        for handler in root_logger.handlers:
            if isinstance(handler, FileHandler):
                filemode = handler.mode
                # remove old ``FileHandler``
                root_logger.removeHandler(handler)
        if logfile == "":
            # disable ``FileHandler``
            pass
        else:
            # add new ``FileHandler``
            handler = FileHandler(logfile, mode=filemode)
            root_logger.addHandler(handler)
