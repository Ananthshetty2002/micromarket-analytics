"""
Logging configuration for Micromarket Analytics Platform

Provides structured logging with JSON formatting for production
and human-readable format for development.
"""
import logging
import sys
import json
from datetime import datetime
from typing import Any, Dict
import os

# Environment-based configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging in production"""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "thread": record.thread,
        }

        # Add extra fields if present
        if hasattr(record, "extra"):
            log_data.update(record.extra)

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data, default=str)


class ColoredFormatter(logging.Formatter):
    """Colored formatter for development"""

    COLORS = {
        "DEBUG": "\033[36m",     # Cyan
        "INFO": "\033[32m",      # Green
        "WARNING": "\033[33m",   # Yellow
        "ERROR": "\033[31m",     # Red
        "CRITICAL": "\033[35m",  # Magenta
        "RESET": "\033[0m"
    }

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.COLORS["RESET"])
        reset = self.COLORS["RESET"]

        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        return f"{color}[{timestamp}] [{record.levelname}] {record.name}: {record.getMessage()}{reset}"


def get_logger(name: str) -> logging.Logger:
    """Get configured logger instance"""
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)

        if ENVIRONMENT == "production":
            formatter = JSONFormatter()
        else:
            formatter = ColoredFormatter()

        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(getattr(logging, LOG_LEVEL.upper()))

    return logger


def log_with_extra(logger: logging.Logger, level: str, message: str, **kwargs):
    """Log with extra context fields"""
    extra = {"extra": kwargs}
    getattr(logger, level.lower())(message, extra=extra)


# Convenience function for access logging
def log_request(logger: logging.Logger, method: str, path: str, status: int, duration_ms: float, **kwargs):
    """Log HTTP request with structured data"""
    log_with_extra(
        logger,
        "info" if status < 400 else "warning",
        f"{method} {path} - {status} ({duration_ms:.2f}ms)",
        method=method,
        path=path,
        status=status,
        duration_ms=round(duration_ms, 2),
        **kwargs
    )


# Create default logger instance
logger = get_logger("micromarket")
