"""logconfig

This is essentially a template which can be copied into a python project and
used to easily achieve a good practice of logging. Modify the local copy as per
the project or site requirements.
"""

import os
import json
import logging.config
import getpass
import threading


default_config = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "simple": {"format": "%(message)s"},
        "extended": {
            "format": "%(asctime)s - %(name)20s - %(levelname)6s - %(message)s"
        },
        "json": {
            "format": "name: %(name)s, level: %(levelname)s, time: %(asctime)s, message: %(message)s"
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "simple",
            "stream": "ext://sys.stdout",
        },
        "local_file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            #  "class": "logging.handlers.FileHandler",
            "level": "DEBUG",
            "formatter": "extended",
            "filename": "debug.log",
            "maxBytes": 1048576,
            "backupCount": 20,
            "encoding": "utf8",
            "delay": True,
        },
        # "graylog_gelf": {
        #     "class": "pygelf.GelfTcpHandler",
        #     "level": "INFO",
        #     # Obviously a DLS-specific configuration: the graylog server address and port
        #     # Use the input "Load Balanced GELF TCP" on graylog2.
        #     "host": "graylog2",
        #     "port": 12201,
        #     "debug": True,
        #     #  The following custom fields will be disabled if setting this False
        #     "include_extra_fields": True,
        #     "username": getpass.getuser(),
        #     "pid": os.getpid(),
        # },
    },
    "loggers": {
        # Fine-grained logging configuration for individual modules or classes
        # Use this to set different log levels without changing 'real' code.
        "MovieApp": {"level": "INFO", "propagate": True, "handlers": ["console"]},
    },
    "root": {
        # Set the level here to be the default minimum level of log record to be produced
        # If you set a handler to level DEBUG you will need to set either this level, or
        # the level of one of the loggers above to DEBUG or you won't see any DEBUG messages
        "level": "INFO",
        # "handlers": ["local_file_handler", "graylog_gelf"],
        "handlers": ["local_file_handler"],
    },
}


class ThreadContextFilter(logging.Filter):
    """A logging context filter to add thread name and ID."""

    def filter(self, record):
        record.thread_id = str(threading.current_thread().ident)
        record.thread_name = str(threading.current_thread().name)
        return True


def setup_logging(
    default_log_config=None, default_level=logging.INFO, env_key="LOG_CFG"
):
    """Setup logging configuration

    Call this only once from the application main() function or __main__ module!

    This will configure the python logging module based on a logging configuration
    in the following order of priority:

       1. Log configuration file found in the environment variable specified in the `env_key` argument.
       2. Log configuration file found in the `default_log_config` argument.
       3. Default log configuration found in the `logconfig.default_config` dict.
       4. If all of the above fails: basicConfig is called with the `default_level` argument.

    Args:
        default_log_config (Optional[str]): Path to log configuration file.
        env_key (Optional[str]): Environment variable that can optionally contain
            a path to a configuration file.
        default_level (int): logging level to set as default. Ignored if a log
            configuration is found elsewhere.

    Returns: None
    """
    dict_config = None
    logconfig_filename = default_log_config
    env_var_value = os.getenv(env_key, None)

    if env_var_value is not None:
        logconfig_filename = env_var_value

    if default_config is not None:
        dict_config = default_config

    if logconfig_filename is not None and os.path.exists(logconfig_filename):
        with open(logconfig_filename, "rt") as f:
            file_config = json.load(f)
        if file_config is not None:
            dict_config = file_config

    if dict_config is not None:
        logging.config.dictConfig(dict_config)
    else:
        logging.basicConfig(level=default_level)
