
import trio
import trio_click as click



@click.group()
def cli():
  pass


@cli.command()
@click.argument("pkg")
@click.option("-t", "--target", default=".")
async def install(pkg, target):
  from bib.installer import Installer
  installer = Installer("https://pypi.org/pypi", target)
  await installer.fetch_pkg(pkg)
