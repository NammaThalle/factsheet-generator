"""Beautiful colored logger for the factsheet generator"""

import logging
import os
import sys
from datetime import datetime

class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors and clean output"""
    
    # Color codes
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green  
        'SUCCESS': '\033[92m',  # Bright Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m',     # Reset
        'BOLD': '\033[1m',      # Bold
        'DIM': '\033[2m'        # Dim
    }
    
    def format(self, record):
        # Get color for log level
        color = self.COLORS.get(record.levelname, '')
        reset = self.COLORS['RESET']
        
        # Format timestamp (date and time, no milliseconds)
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        
        # Format filename:line for VS Code clickability
        filename = os.path.basename(record.pathname)
        location = f"{filename}:{record.lineno}"
        
        # Format: 2025-06-19 12:53:56 [INFO] - file.py:255 - <log msg>
        formatted_msg = (
            f"{timestamp} "
            f"{color}[{record.levelname}]{reset} - "
            f"{location} - "
            f"{record.getMessage()}"
        )
        
        return formatted_msg
    
    def _get_level_icon(self, levelname: str) -> str:
        """Get icon for log level"""
        icons = {
            'DEBUG': 'DEBUG  ',
            'INFO': 'INFO   ',
            'SUCCESS': 'SUCCESS',
            'WARNING': 'WARNING',
            'ERROR': 'ERROR  ',
            'CRITICAL': 'CRITICAL'
        }
        return icons.get(levelname, 'INFO   ')


class FactsheetLogger:
    """Clean, beautiful logger for the factsheet generator"""
    
    def __init__(self, name: str = "factsheet"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Remove all existing handlers
        self.logger.handlers.clear()
        
        # Create console handler with colored formatter
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(ColoredFormatter())
        
        self.logger.addHandler(console_handler)
        
        # Prevent propagation to root logger
        self.logger.propagate = False
        
        # Silence other loggers
        self._silence_external_loggers()
    
    def _silence_external_loggers(self):
        """Silence external library loggers"""
        external_loggers = [
            'urllib3', 'httpx', 'httpcore', 'openai', 'google.auth',
            'google.generativeai', 'requests', 'selenium'
        ]
        
        for logger_name in external_loggers:
            logging.getLogger(logger_name).setLevel(logging.WARNING)
    
    def debug(self, message: str):
        """Log debug message"""
        self.logger.debug(message)
    
    def info(self, message: str):
        """Log info message"""
        self.logger.info(message)
    
    def success(self, message: str):
        """Log success message"""
        # Custom level for success messages
        self.logger.log(25, message)  # Between INFO(20) and WARNING(30)
    
    def warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log error message"""
        self.logger.error(message)
    
    def critical(self, message: str):
        """Log critical message"""
        self.logger.critical(message)
    
    def step(self, step_num: int, message: str):
        """Log a step in the process"""
        self.info(f"Step {step_num}: {message}")
    
    def set_verbose(self, verbose: bool = True):
        """Enable/disable verbose logging"""
        if verbose:
            self.logger.setLevel(logging.DEBUG)
            for handler in self.logger.handlers:
                handler.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)
            for handler in self.logger.handlers:
                handler.setLevel(logging.INFO)


# Global logger instance
logger = FactsheetLogger()

# Add SUCCESS level to logging module
logging.addLevelName(25, 'SUCCESS')