from setuptools import setup

package_name = "artis_gripper_ros2"

setup(
    name=package_name,
    version="0.1.0",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="ARTiS Team",
    maintainer_email="user@example.com",
    description="ROS 2 ARTiS gripper node",
    license="MIT",
    entry_points={
        "console_scripts": ["artis_node = artis_gripper_ros2.artis_node:main"],
    },
)
