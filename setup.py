import os

from setuptools import setup


README_FILE = os.path.join(os.path.dirname(__file__), 'readme.rst')


setup(
    name="vim_python",
    version="0.0.1",
    author="Maik Brendler",
    author_email="sellerieschnitzel@googlemail.com",
    description="",
    long_description=open(README_FILE).read(),
    license="BSD",
    keywords="",
    url="",
    packages=['vim_python'],
    classifiers=[],
)
