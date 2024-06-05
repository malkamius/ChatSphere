import logging
import sys
import re

def strip_ansi_codes(text):
    ansi_escape = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', text)

# Custom formatter that strips ANSI codes
class StripAnsiFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord):
        original = super().format(record)
        return strip_ansi_codes(original)
        
def getLogger(config, loggername: str) -> logging.Logger:
    if config.DEBUG:
        loglevel = logging.DEBUG
    elif config.INFO:
        loglevel = logging.INFO
    else:
        loglevel = logging.ERROR
    # Create a logger
    logger = logging.getLogger(loggername)
    logger.setLevel(loglevel)
    if not logger.hasHandlers():
        # Console handler with colored output
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_format)

        # File handler without colored output
        file_handler = logging.FileHandler('logfile.log')
        file_handler.setLevel(logging.DEBUG)
        file_format = StripAnsiFormatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_format)

        # Add handlers to the logger
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
    
    return logger;