from setuptools import setup

package_name = 'system_monitor_gui'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        # 资源索引标记文件，让 ROS2 能发现这个 ament_python 包
        ('share/ament_index/resource_index/packages',
         ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='you',
    maintainer_email='you@example.com',
    description='用 Qt 小窗口实时显示系统状态的 ROS2 包',
    license='Apache-2.0',
    entry_points={
        # 注册可执行命令：ros2 run system_monitor_gui system_monitor_gui
        'console_scripts': [
            'system_monitor_gui = system_monitor_gui.gui_node:main',
        ],
    },
)
