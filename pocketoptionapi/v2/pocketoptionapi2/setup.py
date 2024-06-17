 
from setuptools import (setup, find_packages)


setup(
    name="pocketoptionapiv2",
    version="2.2",
    packages=find_packages(),
    install_requires=["pylint","requests","websocket-client==0.58","des"],
    include_package_data = True,
    description="Free PoacketOption API for python",
    long_description="Free pocketoptionapi API for python",
    url="https://github.com/theshadow76/PocketOptionAPI",
    author="Vigo Wa;ler",
    author_email="vigopaul05@gmail.com",
    zip_safe=False
)
