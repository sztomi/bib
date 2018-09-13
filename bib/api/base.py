from abc import ABCMeta, abstractmethod
from distutils.version import LooseVersion

class ApiBase(metaclass=ABCMeta):
  def __init__(self, session, auth):
    self.session = session
    self.auth = auth

  async def get(self, path):
    self.log.debug(f"GET {path}")
    return await self.session.get(path=path, auth=self.auth, auth_off_domain=True)

  @abstractmethod
  async def get_releases(self, package):
    pass
