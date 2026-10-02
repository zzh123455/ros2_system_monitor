#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统监控发布节点（包 1）

功能：周期性地采集本机的 CPU 使用率、内存、网络收发等实时信息，
     打包成自定义消息 SystemStatus，发布到 /system_status 话题。

运行：ros2 run system_monitor monitor_publisher.py
"""
import socket

import psutil
import rclpy
from rclpy.node import Node

from system_monitor.msg import SystemStatus


class MonitorPublisher(Node):
    def __init__(self):
        super().__init__('monitor_publisher')

        # 发布频率（Hz），可通过参数发布频率调整，例如：
        #   ros2 run system_monitor monitor_publisher.py --ros-args -p publish_rate:=2.0
        self.declare_parameter('publish_rate', 1.0)
        rate = self.get_parameter('publish_rate').value

        # 创建发布者：消息类型 SystemStatus，话题名 /system_status，队列长度 10
        self.publisher = self.create_publisher(SystemStatus, 'system_status', 10)

        # 定时器：按频率周期触发 publish_status
        self.timer = self.create_timer(1.0 / rate, self.publish_status)

        # cpu_percent(interval=None) 返回的是“自上次调用以来”的平均占用率，
        # 第一次调用总是返回 0.0，所以这里先调用一次做“预热”，让后续取值真实有效。
        psutil.cpu_percent(interval=None)

        self.get_logger().info('监控发布节点已启动，发布话题: /system_status')

    def publish_status(self):
        msg = SystemStatus()

        # 1) 记录信息的时间（ROS2 时间戳）
        msg.stamp = self.get_clock().now().to_msg()

        # 2) 主机名
        msg.hostname = socket.gethostname()

        # 3) CPU 使用率（非阻塞，百分比）
        msg.cpu_percent = psutil.cpu_percent(interval=None)

        # 4) 内存信息
        mem = psutil.virtual_memory()
        msg.mem_percent = mem.percent                      # 使用率 %
        msg.mem_total_mb = mem.total / (1024 * 1024)       # 总大小 MB
        msg.mem_available_mb = mem.available / (1024 * 1024)  # 剩余可用 MB

        # 5) 网络累计收发字节数
        net = psutil.net_io_counters()
        msg.net_recv_bytes = net.bytes_recv
        msg.net_sent_bytes = net.bytes_sent

        # 发布消息
        self.publisher.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = MonitorPublisher()
    try:
        rclpy.spin(node)      # 阻塞，让定时器持续触发
    except KeyboardInterrupt:
        pass                  # 按 Ctrl+C 优雅退出
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
