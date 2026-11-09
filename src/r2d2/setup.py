from glob import glob
import os

from setuptools import setup

package_name = 'r2d2'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'),
            glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*')),
        (os.path.join('share', package_name, 'config'), glob('config/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='kunal',
    maintainer_email='kunaldabbe2003@gmail.com',
    description='R2D2 RViz demo with an animated state publisher',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'state_publisher = r2d2.state_publisher:main',
        ],
    },
)
