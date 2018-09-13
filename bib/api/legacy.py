from .base import ApiBase
from bib.logging import get_logger

from collections import OrderedDict

from pypi_simple import parse_simple_index, parse_filename

import packaging.version
import trio

import re


class LegacyApi(ApiBase):
  def __init__(self, session, auth):
    super().__init__(session, auth)
    self.log = get_logger(__name__)

  async def get_releases(self, package):
    path = f"/{package}"
    resp = await self.get(path)
    data = await trio.run_sync_in_worker_thread(parse_simple_index, resp.text)

    result = {}
    for filename, url in data:
      _, version, dtype = await trio.run_sync_in_worker_thread(parse_filename, filename)
      if dtype == "wheel":
        ver_info = await trio.run_sync_in_worker_thread(packaging.version.parse, version)
        url = url.partition("#")[0]
        result[ver_info] = [url]

    if not result:
      raise RuntimeError(f"No wheel for {package}")

    return OrderedDict(sorted(result.items()))
