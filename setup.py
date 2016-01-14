from setuptools import setup, find_packages

setup(
    name="SatTrack",
    version="0.5",
    author="Ibrahim Ahmed",
    description="Track and visualize satellites and control antenna position",
    packages=find_packages(),
    install_requires=['pyephem', 'lxml', 'pyserial']
)
