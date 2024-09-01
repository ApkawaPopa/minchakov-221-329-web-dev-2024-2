import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = os.getenv('FLASK_DEBUG') == 'True'
    ENV = os.getenv('FLASK_ENV')


if __name__ == '__main__':
    config = Config()
    print(config.SECRET_KEY, config.SQLALCHEMY_DATABASE_URI, config.DEBUG, config.SQLALCHEMY_TRACK_MODIFICATIONS,
          config.ENV)
