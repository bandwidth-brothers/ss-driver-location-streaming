import logging as log


def _setup_logger():
    log.VERBOSE = 5
    log.addLevelName(log.VERBOSE, 'VERBOSE')
    log.Logger.verbose = lambda inst, msg, *args, **kwargs: inst.log(log.VERBOSE, msg, *args, **kwargs)
    log.verbose = lambda msg, *args, **kwargs: log.log(log.VERBOSE, msg, *args, **kwargs)


_setup_logger()
