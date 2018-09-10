from abc import ABCMeta, abstractmethod
from distutils.version import LooseVersion

class ApiBase(metaclass=ABCMeta):
  def __init__(self, session):
    self.session = session

  @abstractmethod
  async def get_releases(self, package):
    pass


class Version(LooseVersion):
  def __hash__(self):
    return hash(str(self))
