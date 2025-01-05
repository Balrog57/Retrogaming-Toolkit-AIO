
from setuptools import setup, find_packages

setup(
    name="Retrogaming-Toolkit-AIO",
    version="1.0.0",
    packages=find_packages(),
    install_requires=open("requirements.txt").readlines(),
    description="Retrogaming-Toolkit-AIO est une interface graphique (GUI) centralisée qui regroupe une collection d'outils Python pour la gestion de jeux, de collections, de fichiers multimédias et bien plus encore.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Balrog57",
    url="https://github.com/Balrog57/Retrogaming-Toolkit-AIO",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
        