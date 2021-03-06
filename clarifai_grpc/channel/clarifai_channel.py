import os

import requests

from clarifai_grpc.channel.grpc_json_channel import GRPCJSONChannel
from clarifai_grpc.grpc.api import service_pb2_grpc


RETRIES = 2  # if connections fail retry a couple times.
CONNECTIONS = 20  # number of connections to maintain in pool.

wrap_response_deserializer = None


def _response_deserializer_for_json(response_deserializer):
  return response_deserializer


def _response_deserializer_for_grpc(response_deserializer):
  return response_deserializer.FromString


class ClarifaiChannel:
  @classmethod
  def get_json_channel(
      cls,
      api_key=os.environ.get('CLARIFAI_API_KEY', 'no_key'),
      base_url=os.environ.get('CLARIFAI_API_BASE', 'https://api.clarifai.com')
  ):
    global wrap_response_deserializer
    wrap_response_deserializer = _response_deserializer_for_json

    session = cls._make_requests_session()

    return GRPCJSONChannel(session=session, key=api_key, base_url=base_url)

  @staticmethod
  def _make_requests_session():
    http_adapter = requests.adapters.HTTPAdapter(
      max_retries=RETRIES, pool_connections=CONNECTIONS, pool_maxsize=CONNECTIONS)

    session = requests.Session()
    session.mount('http://', http_adapter)
    session.mount('https://', http_adapter)
    return session

  @staticmethod
  def get_grpc_channel():
    global wrap_response_deserializer
    wrap_response_deserializer = _response_deserializer_for_grpc

    return service_pb2_grpc.grpc.secure_channel(
      'api-grpc.clarifai.com:18081',
      service_pb2_grpc.grpc.ssl_channel_credentials()
    )

  @staticmethod
  def get_insecure_grpc_channel():
    global wrap_response_deserializer
    wrap_response_deserializer = _response_deserializer_for_grpc

    return service_pb2_grpc.grpc.insecure_channel('api-grpc.clarifai.com:18080')
