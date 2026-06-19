from setuptools import find_packages, setup

setup(
    name="artis_gripper",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["dynamixel-sdk", "pyserial", "pyyaml"],
    entry_points={"console_scripts": ["artis-cli=artis_gripper.cli:main"]},
)
