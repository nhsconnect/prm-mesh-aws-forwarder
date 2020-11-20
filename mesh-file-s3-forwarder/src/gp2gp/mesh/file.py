from defusedxml.ElementTree import parse, ParseError
from datetime import datetime

EVENT_TYPE_TRANSFER = "TRANSFER"
EVENT_STATUS_SUCCESS = "SUCCESS"


class MeshFile:
    def __init__(self, path):
        self.path = path
        self._ctl_path = _build_ctl_filepath(dat_file_path=path)

    def __eq__(self, other):
        if not isinstance(other, MeshFile):
            return NotImplemented

        return self.path == other.path

    def read_delivery_date(self):
        try:
            status_record = self._read_ctl_status_record()
            self._validate_status_record(status_record)
            parsed_date = _parse_date_from_status_record(status_record)
            return parsed_date
        except AttributeError as e:
            raise UnexpectedControlFileStructure(self._ctl_path) from e

    def _read_ctl_status_record(self):
        try:
            ctl_xml = parse(self._ctl_path).getroot()
            return ctl_xml.find("StatusRecord")
        except ParseError as e:
            raise InvalidControlFileXML(self._ctl_path) from e

    def _validate_status_record(self, status_record):
        event_type = status_record.find("Event").text
        event_status = status_record.find("Status").text

        if event_type != EVENT_TYPE_TRANSFER:
            raise UnexpectedControlEvent(self._ctl_path, event_type)

        if event_status != EVENT_STATUS_SUCCESS:
            raise UnsuccessfulControlStatus(self._ctl_path, event_status)


def _parse_date_from_status_record(status_record):
    date_string = status_record.find("DateTime").text
    return datetime.strptime(date_string, "%Y%m%d%H%M%S")


def _build_ctl_filepath(dat_file_path):
    file_name = dat_file_path.stem
    return dat_file_path.parent / f"{file_name}.ctl"


class MeshFileException(Exception):
    pass


class UnexpectedControlEvent(MeshFileException):
    def __init__(self, path, event_type):
        super().__init__(f"Unexpected event type in CTL file, path: {path}, event: {event_type}")


class UnsuccessfulControlStatus(MeshFileException):
    def __init__(self, path, event_status):
        super().__init__(f"Unsuccessful status in CTL file, path: {path}, status: {event_status}")


class InvalidControlFileXML(MeshFileException):
    def __init__(self, path):
        super().__init__(f"Invalid XML in CTRL file, {path}")


class UnexpectedControlFileStructure(MeshFileException):
    def __init__(self, path):
        super().__init__(f"Unexpected XML structure in CTRL file, {path}")
