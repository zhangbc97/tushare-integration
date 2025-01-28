import logging

from tushare_integration.commands import app

logging.basicConfig(level=logging.INFO)


def main():
    app()


if __name__ == '__main__':
    main()
