
import trio
import trio_click as click



@click.group()
def cli():
  pass


@cli.command()
@click.argument("pkg")
@click.option("-t", "--target", default=".")
@click.option("-i", "--index-url", default="https://pypi.org/simple")
async def install(pkg, target, index_url):
  from bib.installer import Installer
  installer = Installer(index_url, target)
  await installer.fetch_pkg(pkg)
