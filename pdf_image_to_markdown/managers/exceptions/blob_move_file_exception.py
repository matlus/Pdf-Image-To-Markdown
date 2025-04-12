import logging
from typing import Any

from pdf_image_to_markdown.managers.exceptions.application_base_exception import ApplicationBaseException, ExceptionAction, LogEvent


class BlobMoveFileException(ApplicationBaseException):
    def __init__(self, message: str, log_event: LogEvent, **context_data: dict[str, Any]):
        super().__init__(message, log_event, **context_data)

    @property
    def action(self) -> ExceptionAction:
        return ExceptionAction.ManualReattemptAutomatedIngestion

    @property
    def severity(self) -> int:
        return logging.ERROR

    @property
    def reason(self) -> str:
        return "Error moving file from one folder to another in blob storage."

    @property
    def http_status_code(self) -> int:
        return 500
