from setuptools import setup

VERSION = "0.3.0"

requirements = ["websocket-client"]

def readme():
    with open('README.md') as f:
        return f.read()

setup(
    name="pusherclient",
    version=VERSION,
    description="Pusher websocket client for python",
    long_description=readme(),
    keywords="pusher websocket client",
    author="Erik Kulyk",
    author_email="e.kulyk@gmail.com",
    license="MIT",
    url="https://github.com/ekulyk/PythonPusherClient",
    install_requires=requirements,
    packages=["pusherclient"],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries ',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
