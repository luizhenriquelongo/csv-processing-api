import os

from app import create_app

app = create_app(os.getenv("CONFIG_CLASS", "config.ProductionConfig"))
app.app_context().push()

if __name__ == "__main__":
    app.run()
