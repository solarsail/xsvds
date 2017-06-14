import logging

conf_dict = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(asctime)s [%(levelname)s] %(name)s | %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': logging.DEBUG,
            'formatter': 'simple',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'class': 'logging.FileHandler',
            'level': logging.DEBUG,
            'formatter': 'simple',
            'filename': 'xsvds.log'
        }
    },
    'loggers': {
        'vds': {
            'level': logging.DEBUG,
            'handlers': ['console', 'file']
        }
    }
}
