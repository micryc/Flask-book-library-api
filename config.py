import os
from dotenv import load_dotenv
from pathlib import Path as pt
# from sqlalchemy import URL
# from sqlalchemy import create_engine

# url_object = URL.create(
#     "mysql+pymysql",
#     username="michal",
#     password="0308@1998Nw",  # plain (unescaped) text
#     host="localhost",
#     database="bookapi_ser",
# )
#
# engine = create_engine(url_object)

base_dir = pt(__file__).resolve().parent
env_file = base_dir / '.env'
load_dotenv(env_file)
# base_dir = pt.cwd()
# env_file = base_dir / pt(".env")
# load_dotenv(env_file)


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PER_PAGE = 5
    JWT_EXPIRED_MINUTES = 30




