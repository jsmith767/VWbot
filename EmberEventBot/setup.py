from setuptools import setup, find_packages

setup(
    name="EmberEventBot",
    version="0.1.0",
    packages=find_packages(include=["EmberEventBot", "EmberEventBot.*"]),
    install_requires=[
        "python-telegram-bot",
        "pytz",
        "httpx",  # add other dependencies here
    ],
    entry_points={
        "console_scripts": [
            "ember-event-bot = EmberEventBot.__main__:main",
        ],
    },
    include_package_data=True,
    description="A Telegram bot for event management",
    author="Your Name",
    author_email="youremail@example.com",
    url="https://github.com/yourusername/EmberEventBot",
)
