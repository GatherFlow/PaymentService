
from app import start_app

from utils.logger import setup_logger
from app.config import LOGS_DIR, LOGS_LEVEL


def main():
    setup_logger(LOGS_DIR, LOGS_LEVEL)
    start_app()


if __name__ == '__main__':
    main()
