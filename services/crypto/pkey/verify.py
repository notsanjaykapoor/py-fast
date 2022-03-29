from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from dataclasses import dataclass
from typing import Any

import base64
import logging

@dataclass
class Struct:
  code: int
  errors: list[str]

class PkeyVerify:
  def __init__(self, public_key: Any, data: str, signature: str):
    self.public_key = public_key
    self.data = data
    self.signature = signature

    self.data_encoding = "utf-8"
    self.logger = logging.getLogger("console")

  def call(self):
    struct = Struct(0, [])

    self.logger.info(f"{__name__}")

    try:
      # convert data str to bytes
      data_bytes = self.data.encode(self.data_encoding)

      # convert signature from base64 string to bytes
      signature_bytes = base64.b64decode(self.signature)

      self.public_key.verify(
        signature_bytes,
        data_bytes,
        ec.ECDSA(hashes.SHA256()),
      )
    except Exception as e:
      struct.code = 500
      self.logger.error(f"{__name__} {e}")

    return struct
