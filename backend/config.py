import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@db:5432/univesp"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False,
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY","DIpjndzt3c7pRgkbV8mu5R6ZYxSFLUbJ" )

class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    TESTING = True
    JWT_SECRET_KEY = "cU2vefZwrQ8/in2VPeY/IyImRYTaMFX9kfUyCbSWAqY="
