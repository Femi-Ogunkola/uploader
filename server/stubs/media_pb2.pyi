from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class VideoChunk(_message.Message):
    __slots__ = ("data", "chunk_index", "is_last_chunk")
    DATA_FIELD_NUMBER: _ClassVar[int]
    CHUNK_INDEX_FIELD_NUMBER: _ClassVar[int]
    IS_LAST_CHUNK_FIELD_NUMBER: _ClassVar[int]
    data: bytes
    chunk_index: int
    is_last_chunk: bool
    def __init__(self, data: _Optional[bytes] = ..., chunk_index: _Optional[int] = ..., is_last_chunk: bool = ...) -> None: ...

class Status(_message.Message):
    __slots__ = ("status", "message", "progress")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    PROGRESS_FIELD_NUMBER: _ClassVar[int]
    status: str
    message: str
    progress: int
    def __init__(self, status: _Optional[str] = ..., message: _Optional[str] = ..., progress: _Optional[int] = ...) -> None: ...

class UploadVideoResponse(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: Status
    def __init__(self, status: _Optional[_Union[Status, _Mapping]] = ...) -> None: ...
