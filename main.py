import click
from sys import exit as s_exit


@click.command()
@click.option("-a", "--algorithm", default=None,
              help="Load algorithm from .py file")
@click.option("-m", "--map", default=None,
              help="Load map from .mc file")
@click.option("-r", "--rule", default=None,
              help="Load rule from .rule file")
@click.option("-p", "--pattern", default=None,
              help="Load pattern from .mc file")
@click.option("-g", "--gui", is_flag=True, default=False,
              help="Use gui. Default is false")
def main(algorithm, map, pattern, rule, gui):
    if gui:
        raise NotImplementedError("Sorry, but now gui is not implemented")
    return 0


if __name__ == '__main__':
    s_exit(main())
