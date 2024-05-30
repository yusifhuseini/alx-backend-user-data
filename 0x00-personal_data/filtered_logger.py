#!/usr/bin/env python3
"""Handles data filtering and logging operations."""

import logging
import os
import re
import mysql.connector
from typing import List


PII_FIELDS = ('name', 'email', 'phone', 'ssn', 'password')


def filter_datum(fields: List[str], redaction: str, message: str, separator: str) -> str:
    """Obfuscates PII fields in a log message.

    Args:
        fields: List of fields to obfuscate.
        redaction: String to replace the field value with.
        message: Log message to filter.
        separator: Field separator character.

    Returns:
        Filtered log message.
    """
    for field in fields:
        message = re.sub(rf"{field}=.*?{separator}", f"{field}={redaction}{separator}", message)
    return message


class RedactingFormatter(logging.Formatter):
    """Redacts specified fields in log records."""

    REDACTION = "***"
    FORMAT = "[HOLBERTON] %(name)s %(levelname)s %(asctime)-15s: %(message)s"
    SEPARATOR = ";"

    def __init__(self, fields: List[str]):
        super().__init__(self.FORMAT)
        self.fields = fields

    def format(self, record: logging.LogRecord) -> str:
        """Filters and formats log records."""
        record.msg = filter_datum(self.fields, self.REDACTION, record.msg, self.SEPARATOR)
        return super().format(record)


def get_logger() -> logging.Logger:
    """Creates a logger with PII redaction."""
    logger = logging.getLogger("user_data")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(RedactingFormatter(PII_FIELDS))
    logger.addHandler(stream_handler)
    return logger


def get_db() -> mysql.connector.connection.MySQLConnection:
    """Connects to the MySQL database."""
    db_host = os.getenv("PERSONAL_DATA_DB_HOST", "localhost")
    db_name = os.getenv("PERSONAL_DATA_DB_NAME", "")
    db_user = os.getenv("PERSONAL_DATA_DB_USERNAME", "root")
    db_pwd = os.getenv("PERSONAL_DATA_DB_PASSWORD", "")

    return mysql.connector.connect(
        host=db_host,
        database=db_name,
        user=db_user,
        password=db_pwd
    )


def main():
    """Retrieves and displays filtered user data from the database."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users;")

    logger = get_logger()

    for row in cursor:
        row_dict = {
            'name': row[0], 'email': row[1], 'phone': row[2], 
            'ssn': row[3], 'password': row[4], 'ip': row[5], 
            'last_login': row[6], 'user_agent': row[7]
        }
        message = "; ".join([f"{k}={v}" for k, v in row_dict.items()])
        logger.info(message)


if __name__ == "__main__":
    main()
