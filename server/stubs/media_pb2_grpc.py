# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

import media_pb2 as media__pb2

GRPC_GENERATED_VERSION = '1.70.0'
GRPC_VERSION = grpc.__version__
_version_not_supported = False

try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True

if _version_not_supported:
    raise RuntimeError(
        f'The grpc package installed is at version {GRPC_VERSION},'
        + f' but the generated code in media_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class VideoUploadServiceStub(object):
    """Video upload service definition with streaming.
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.UploadVideo = channel.stream_stream(
                '/videoUpload.VideoUploadService/UploadVideo',
                request_serializer=media__pb2.VideoChunk.SerializeToString,
                response_deserializer=media__pb2.UploadVideoResponse.FromString,
                _registered_method=True)
        self.StreamVideo = channel.unary_stream(
                '/videoUpload.VideoUploadService/StreamVideo',
                request_serializer=media__pb2.VideoRequest.SerializeToString,
                response_deserializer=media__pb2.VideoChunk.FromString,
                _registered_method=True)


class VideoUploadServiceServicer(object):
    """Video upload service definition with streaming.
    """

    def UploadVideo(self, request_iterator, context):
        """RPC method for streaming video data and uploading it.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def StreamVideo(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_VideoUploadServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'UploadVideo': grpc.stream_stream_rpc_method_handler(
                    servicer.UploadVideo,
                    request_deserializer=media__pb2.VideoChunk.FromString,
                    response_serializer=media__pb2.UploadVideoResponse.SerializeToString,
            ),
            'StreamVideo': grpc.unary_stream_rpc_method_handler(
                    servicer.StreamVideo,
                    request_deserializer=media__pb2.VideoRequest.FromString,
                    response_serializer=media__pb2.VideoChunk.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'videoUpload.VideoUploadService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('videoUpload.VideoUploadService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class VideoUploadService(object):
    """Video upload service definition with streaming.
    """

    @staticmethod
    def UploadVideo(request_iterator,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.stream_stream(
            request_iterator,
            target,
            '/videoUpload.VideoUploadService/UploadVideo',
            media__pb2.VideoChunk.SerializeToString,
            media__pb2.UploadVideoResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def StreamVideo(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(
            request,
            target,
            '/videoUpload.VideoUploadService/StreamVideo',
            media__pb2.VideoRequest.SerializeToString,
            media__pb2.VideoChunk.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
