from asyncio import run as aiorun

import typer


def main(name: str = typer.Argument("Wade Wilson")):
    async def _main():
        typer.echo(f"Hello {name}")


    aiorun(_main())


if __name__ == "__main__":
    typer.run(main)
