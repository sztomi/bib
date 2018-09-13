from .base import ApiBase, Version
from bib.logging import get_logger

from collections import OrderedDict

import packaging.version


class JsonApi(ApiBase):
  def __init__(self, session):
    super().__init__(session)
    self.log = get_logger(__name__)

  async def get_releases(self, package):
    path = f"/{package}/json"
    self.log.debug(f"Fetching {path}")
    resp = await self.session.get(path=path)
    data = resp.json()

    result = {}
    for version, releases in data["releases"].items():
      urls = []
      for release in releases:
        urls.append(release["url"])
      ver_info = packaging.version.parse(version)
      result[ver_info] = urls
    return OrderedDict(sorted(result.items()))
