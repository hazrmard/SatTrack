from setuptools import setup, find_packages
from subprocess import call

#os.environ["DISTUTILS_USE_SDK"]="1"
#os.environ["MSSdk"]="1"

setup(
    name="SatTrack",
    version="0.5",
    author="Ibrahim Ahmed",
    description="Track and visualize satellites and control antenna position",
    packages=find_packages(),
    install_requires=['six', 'pyserial', 'requests', 'python-dateutil'],
    include_package_data = True,
)

#installing using install_requires in setup() does not seem to work
# pip shoulf be in system path variable
print 'INSTALLING PYEPHEM'
call("pip install pyephem")
