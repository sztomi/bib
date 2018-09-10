
import trio
import trio_click as click



@click.group()
def cli():
  pass


@cli.command()
@click.argument("pkg")
async def install(pkg):
  from bib.installer import Installer
  installer = Installer("https://pypi.org/pypi", "tmp")
  await installer.fetch_pkg(pkg)
