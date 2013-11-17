from setuptools import setup

VERSION = "0.1.0"

setup(
    name="pusherclient",
    version=VERSION,
    description="Pusher websocket client for python",
    author="Erik Kulyk",
    author_email="e.kulyk@gmail.com",
    license="",
    url="",
    requires=["websocket"],
    packages=["pusherclient"],
)
