import os

from app import create_app

app = create_app(os.getenv("CONFIG_CLASS", "config.ProductionConfig"))


if __name__ == "__main__":
    app.run()
