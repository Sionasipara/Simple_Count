from setuptools import find_packages, setup

package_name = 'simple_counter'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Sunny Shi',
    maintainer_email='sionasipara5@gmail.com',
    description='Examples of minimal publisher/subscriber using rclpy',
    license='Apache License 2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
                'talker = simple_counter.publisher_node:main',
                'listener = simple_counter.subscriber_node:main',
                'draw_shape = simple_counter.draw_shape:main',
        ],
    },
)
