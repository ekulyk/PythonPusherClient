from setuptools import setup
import sys

VERSION = "0.2.0"

requirements = ["websocket-client"]

setup(
    name="pusherclient",
    version=VERSION,
    description="Pusher websocket client for python",
    author="Erik Kulyk",
    author_email="e.kulyk@gmail.com",
    license="",
    url="",
    install_requires=requirements,
    packages=["pusherclient"],
)
