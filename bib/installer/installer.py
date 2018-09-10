from bib.api import JsonApi
from bib.logging import get_logger

import trio
import asks
import pkginfo
import re


req_rgx = re.compile(r"^(?P<req>[\w\-_]+)[ ;]")


class Installer:
  log = get_logger(__name__)
  def __init__(self, index_url, target_dir):
    asks.init("trio")
    self.index_url = index_url
    self.target_dir = trio.Path(target_dir)
    self.session = asks.Session(connections=8)
    self.session.base_location = index_url
    self.api = JsonApi(self.session)

  async def _fetch_json(self, pkg):
    releases = await self.api.get_releases(pkg)
    last_ver = next(reversed(releases))
    return releases[last_ver][0]

  def _get_requires(self, wheel):
    meta = pkginfo.Wheel(wheel)
    reqs = []
    for r in meta.requires_dist:
      match = req_rgx.match(r)
      if match:
        yield match.group("req")

  async def fetch_pkg(self, pkg):
    self.log.debug(f"Downloading {pkg}")
    whl_url = await self._fetch_json(pkg)
    whl_resp = await asks.get(whl_url, stream=True)
    fname = whl_url.split("/")[-1]
    output_name = trio.Path(self.target_dir / fname)
    async with await output_name.open("wb") as wheel:
      async with whl_resp.body:
        async for chunk in whl_resp.body:
          await wheel.write(chunk)
    for r in self._get_requires(output_name):
      async with trio.open_nursery() as nursery:
        nursery.start_soon(self.fetch_pkg, r)

