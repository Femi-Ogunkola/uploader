# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: media.proto
# Protobuf Python Version: 5.29.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    29,
    0,
    '',
    'media.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0bmedia.proto\x12\x0bvideoUpload\"F\n\nVideoChunk\x12\x0c\n\x04\x64\x61ta\x18\x01 \x01(\x0c\x12\x13\n\x0b\x63hunk_index\x18\x02 \x01(\x03\x12\x15\n\ris_last_chunk\x18\x03 \x01(\x08\";\n\x06Status\x12\x0e\n\x06status\x18\x01 \x01(\t\x12\x0f\n\x07message\x18\x02 \x01(\t\x12\x10\n\x08progress\x18\x03 \x01(\x03\":\n\x13UploadVideoResponse\x12#\n\x06status\x18\x01 \x01(\x0b\x32\x13.videoUpload.Status2b\n\x12VideoUploadService\x12L\n\x0bUploadVideo\x12\x17.videoUpload.VideoChunk\x1a .videoUpload.UploadVideoResponse(\x01\x30\x01\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'media_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_VIDEOCHUNK']._serialized_start=28
  _globals['_VIDEOCHUNK']._serialized_end=98
  _globals['_STATUS']._serialized_start=100
  _globals['_STATUS']._serialized_end=159
  _globals['_UPLOADVIDEORESPONSE']._serialized_start=161
  _globals['_UPLOADVIDEORESPONSE']._serialized_end=219
  _globals['_VIDEOUPLOADSERVICE']._serialized_start=221
  _globals['_VIDEOUPLOADSERVICE']._serialized_end=319
# @@protoc_insertion_point(module_scope)
