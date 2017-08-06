import distutils.core
import os

with open("README.md") as readme_fp:
    long_description = readme_fp.read()

distutils.core.setup(
    name="kenburns",
    version="0.0.1",
    packages=["kenburns"],
    author="Ivan Helmot",
    author_email="mr.ivan.helmot@gmail.com",
    url="https://github.com/helmot/kenburns",
    license="http://www.apache.org/licenses/LICENSE-2.0",
    description="Simple script to make a video by adding kenburns effect with some text to an image",
    long_description=long_description)