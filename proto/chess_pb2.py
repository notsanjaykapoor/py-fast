# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: chess.proto
# Protobuf Python Version: 4.25.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0b\x63hess.proto\x12\x06stream\"+\n\x07Message\x12\x0f\n\x07subject\x18\x01 \x01(\t\x12\x0f\n\x07message\x18\x02 \x01(\t2;\n\x06Stream\x12\x31\n\x07message\x12\x0f.stream.Message\x1a\x0f.stream.Message\"\x00(\x01\x30\x01\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'chess_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_MESSAGE']._serialized_start=23
  _globals['_MESSAGE']._serialized_end=66
  _globals['_STREAM']._serialized_start=68
  _globals['_STREAM']._serialized_end=127
# @@protoc_insertion_point(module_scope)
