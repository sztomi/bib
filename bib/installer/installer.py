from bib.api import LegacyApi
from bib.logging import get_logger

import trio
import asks
import pkginfo
import re
import random


req_rgx = re.compile(r"^(?P<req>[\w\-_]+)[ ;]")


class Installer:
  log = get_logger(__name__)
  def __init__(self, index_url, target_dir):
    asks.init("trio")
    self.index_url = index_url
    if "@" in index_url:
      from asks import BasicAuth, DigestAuth
      index_url = index_url[8:]
      parts = index_url.partition("@")
      user, pw = parts[0].split(":")
      self.auth = BasicAuth((user, pw))
      # TODO: use the original protocol instead of hardcoded https
      self.index_url = "https://" + parts[2]
    else:
      self.auth = None
    self.target_dir = trio.Path(target_dir)
    self.session = asks.Session(connections=8)
    self.session.base_location = self.index_url
    self.log.debug(f"Base URL: {self.session.base_location}")
    self.api = LegacyApi(self.session, self.auth)

  async def _fetch_metadata(self, pkg):
    self.log.debug(f"Getting metadata of {pkg}")
    releases = await self.api.get_releases(pkg)
    last_ver = next(reversed(releases), None)
    if not last_ver:
      return None
    return releases[last_ver][0]

  async def _get_requires(self, wheel):
    meta = await trio.run_sync_in_worker_thread(pkginfo.Wheel, wheel)
    for r in meta.requires_dist:
      match = req_rgx.match(r)
      if match:
        yield match.group("req")

  async def _fetch_pkg(self, url):
    whl_resp = await asks.get(url, stream=True)
    fname = url.split("/")[-1]
    output_name = trio.Path(self.target_dir / fname)
    async with await output_name.open("wb") as wheel:
      async with whl_resp.body:
        async for chunk in whl_resp.body:
          await wheel.write(chunk)
    return output_name

  async def fetch_pkg(self, pkg):
    url = await self._fetch_metadata(pkg)
    output_name = await self._fetch_pkg(url)

    async with trio.open_nursery() as nursery:
      async for r in self._get_requires(output_name):
        self.log.debug(f"Queuing {r}")
        nursery.start_soon(self.fetch_pkg, r)

