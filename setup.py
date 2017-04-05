# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from asyncftp import __version__

setup(
    name="asyncftp",
    version=__version__,
    description="Just an another ftp server",
    long_description=open("README.md").read(),
    keywords="async, curio, ftp, server",
    author="helloqiu",
    author_email="helloqiu95@gmail.com",
    url="https://github.com/helloqiu/AsyncFTP",
    packages=find_packages(),
    entry_points={
        "console_scripts": ["asyncftpd=asyncftp.cli:parse"],
    },
    install_requires=open("requirements.txt").readlines(),
    license="MIT License",
    classifiers=[
        "Development Status :: 1 - Planning",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS",
        "Operating System :: POSIX",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python"
    ],
)
