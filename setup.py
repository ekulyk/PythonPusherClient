from setuptools import setup

VERSION = "0.2.0"

setup(
    name="pusherclient",
    version=VERSION,
    description="Pusher websocket client for python",
    author="Erik Kulyk",
    author_email="e.kulyk@gmail.com",
    license="",
    url="",
    install_requires=["websocket-client"],
    packages=["pusherclient"],
)
