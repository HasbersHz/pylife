import os
import click
import sys


@click.command()
@click.option("-a", "--algorithm", default="",
              help="Load algorithm from .py file")
@click.option("-r", "--rule", default="",
              help="Load rule from .rule file")
@click.option("-p", "--pattern", default="",
              help="Load pattern from .mc file")
@click.option("-g", "--gui", is_flag=True, default=False,
              help="Use gui. Default is false")
def main(algorithm, pattern, rule, gui):
    if gui:
        raise NotImplementedError("Sorry, but now gui is not implemented")
    if os.access(pattern, os.R_OK):
        ...
    elif os.access(algorithm, os.R_OK):
        ...
    elif os.access(rule, os.R_OK):
        ...

    return 0


if __name__ == '__main__':
    sys.exit(main())
