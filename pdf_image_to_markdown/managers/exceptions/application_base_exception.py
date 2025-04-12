import json
import logging
import traceback
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from types import TracebackType
from typing import ClassVar

# Type aliases for improved readability and maintainability
CustomDimensionsDict = dict[str, str | int | bool | None]
ContextualDataDict = dict[str, CustomDimensionsDict]


class ExceptionAction(Enum):
    ManualIngestionUnforseen = "ManualIngestionUnforseen"
    ManualIngestionAnticipated = "ManualIngestionAnticipated"
    ManualReattemptAutomatedIngestion = "ManualReattemptAutomatedIngestion"
    DependecyMissingActionRequired = "DependecyMissingActionRequired"
    UserActionRequired = "UserActionRequired"
    NoActionNeeded = "NoActionNeeded"


@dataclass(frozen=True)
class ExceptionCause:
    exception_type: str
    message: str
    traceback: TracebackType | None = None

    def to_dict(self) -> dict[str, str]:
        result: dict[str, str] = {"exception_type": self.exception_type, "message": self.message}
        if self.traceback:
            result["traceback"] = "".join(traceback.format_tb(self.traceback))
        return result


class LogEvent(Enum):
    pass


class ApplicationBaseException(Exception):  # noqa: N818
    CUSTOM_DIMENSIONS: ClassVar[str] = "custom_dimensions"

    severity_levels_dict: ClassVar[dict[int, str]] = {
        0: "NotSet",
        10: "Debug",
        20: "Information",
        30: "Warning",
        40: "Error",
        50: "Critical",
    }

    def __init__(self, message: str, log_event: LogEvent, context_data: dict[str, str | int | bool | None] | None = None) -> None:
        super().__init__(message)
        self._message: str = message
        self._log_event: LogEvent = log_event

        self._contextual_data = self._build_base_contextual_data()

        if context_data:
            self.add_contextual_data(context_data)

    def _build_base_contextual_data(self) -> ContextualDataDict:
        base_data: CustomDimensionsDict = {
            "ApplicationName": "Structured Logging",
            "ExceptionType": type(self).__name__,
            "Message": self.message,
            "Action": self.action.value,
            "Reason": self.reason,
            "LogEvent": self.log_event.value,
            "Severity": self.get_severity_str(self.severity),
            "HttpStatusCode": self.http_status_code,
        }

        if self.cause:
            base_data["CausedBy"] = self.cause.exception_type
            base_data["Cause"] = self.cause.message

        return {self.CUSTOM_DIMENSIONS: base_data}

    @property
    def message(self) -> str:
        return self._message

    @property
    def action(self) -> ExceptionAction:
        return ExceptionAction.ManualIngestionUnforseen

    @property
    def reason(self) -> str:
        return "An error occurred"

    @property
    def log_event(self) -> LogEvent:
        return self._log_event

    @property
    def severity(self) -> int:
        return logging.ERROR

    @property
    def http_status_code(self) -> int:
        return 400

    @property
    def cause(self) -> ExceptionCause | None:
        cause = getattr(self, "__cause__", None)
        if cause is not None:
            return ExceptionCause(exception_type=type(cause).__name__, message=str(cause), traceback=cause.__traceback__)
        return None

    @property
    def contextual_data(self) -> ContextualDataDict:
        return self._contextual_data

    def add_contextual_data(self, value: dict[str, str | int | bool | None]) -> None:
        self._contextual_data[self.CUSTOM_DIMENSIONS].update(value)

    @staticmethod
    def get_severity_str(severity_level: int) -> str:
        if severity_level in ApplicationBaseException.severity_levels_dict:
            return ApplicationBaseException.severity_levels_dict[severity_level]
        raise ValueError(
            f"Invalid severity level: {severity_level}. "
            f"Possible values are {', '.join(map(str, ApplicationBaseException.severity_levels_dict.keys()))}."
        )

    def _format_exception_data(self, include_traceback: bool = False) -> list[str]:
        data = self.contextual_data[self.CUSTOM_DIMENSIONS].copy()

        lines: list[str] = [f"{key}: {value}" for key, value in data.items()]

        if self.cause:
            lines.extend(
                [
                    "",
                    "Cause Information:",
                    f"CausedBy: {self.cause.exception_type}",
                    f"Cause: {self.cause.message}",
                ]
            )
            if include_traceback and self.cause.traceback:
                lines.append(f"Cause Traceback: {self.cause.traceback}")

        # # Get context_data separately if it exists
        # if "context_data" in data:
        #     context_data = data["context_data"]
        #     if isinstance(context_data, dict):
        #         lines.extend(
        #             [
        #                 "",  # Empty line before context section
        #                 "Contextual Data:",
        #             ]
        #         )
        #         lines.extend(f"  {key}: {value}" for key, value in context_data.items())

        return lines

    @staticmethod
    def get_exception_details(e: Exception, message: str) -> str:
        if isinstance(e, ApplicationBaseException):
            lines = e._format_exception_data(include_traceback=True)
        else:
            lines = [f"ExceptionType: {type(e).__name__}", f"Message: {str(e)}"]
            attributes = [attr for attr in dir(e) if not attr.startswith("__") and not callable(getattr(e, attr))]
            if attributes:
                lines.extend(
                    [
                        "",
                        "Exception Attributes:",
                    ]
                )
                lines.extend(f"  {attr}: {getattr(e, attr)}" for attr in attributes)

        lines.extend(
            [
                "",
                traceback.format_exc(),
            ]
        )

        return "\n".join(lines)

    def to_string(self, include_traceback: bool = False) -> str:
        lines = self._format_exception_data(include_traceback)

        lines.extend(
            [
                "",
                traceback.format_exc(),
            ]
        )

        return "\n".join(lines)

    def to_json(self) -> str:
        return json.dumps(self, cls=ApplicationBaseExceptionJsonEncoder, indent=2)


class ApplicationBaseExceptionJsonEncoder(json.JSONEncoder):
    def default(self, o: object) -> object:  # noqa: PLR0911
        """The parameter `o` is the object to serialize. Base class calls it that so we're stuck with it."""
        if isinstance(o, ApplicationBaseException):
            return self._handle_application_exception(o)
        if isinstance(o, ExceptionCause):
            return o.to_dict()
        if isinstance(o, Enum):
            return o.value
        if isinstance(o, Path):
            return str(o)
        if isinstance(o, datetime):
            return o.isoformat()
        if isinstance(o, Exception):
            return {"ExceptionType": type(o).__name__, "Message": str(o)}

        return super().default(o)

    def _handle_application_exception(self, app_exception: ApplicationBaseException) -> Mapping[str, object]:
        result_dict = app_exception.contextual_data[ApplicationBaseException.CUSTOM_DIMENSIONS].copy()

        if app_exception.cause:
            result_dict["CausedBy"] = app_exception.cause.exception_type
            result_dict["Cause"] = app_exception.cause.message

        return result_dict
