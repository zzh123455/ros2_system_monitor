#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统状态显示界面节点（包 2）

功能：订阅 /system_status 话题，在 Qt 小窗口里实时显示系统信息。

运行：ros2 run system_monitor_gui system_monitor_gui

关键点：用 QTimer 周期调用 rclpy.spin_once()，让 ROS2 的消息回调与
Qt 界面跑在同一个线程里，因此可以在回调里直接更新控件，无需额外信号槽。
"""
import sys
from datetime import datetime

import rclpy
from rclpy.node import Node
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QGridLayout,
    QLabel,
    QGroupBox,
    QVBoxLayout,
)

from system_monitor.msg import SystemStatus


def fmt_bytes(n):
    """把字节数格式化成易读的 B/KB/MB/GB 字符串。"""
    value = float(n)
    for unit in ('B', 'KB', 'MB', 'GB', 'TB'):
        if value < 1024.0 or unit == 'TB':
            return f'{value:.2f} {unit}'
        value /= 1024.0
    return f'{value:.2f} TB'


class SystemMonitorWindow(QMainWindow):
    """纯界面部分：负责布局与显示，不关心 ROS2。"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle('系统状态监控')
        self.resize(480, 360)

        # 动态更新的标签，后面 update_status 里会逐个赋值
        self.lbl_time = QLabel('-')
        self.lbl_host = QLabel('-')
        self.lbl_cpu = QLabel('-')
        self.lbl_mem_percent = QLabel('-')
        self.lbl_mem_total = QLabel('-')
        self.lbl_mem_avail = QLabel('-')
        self.lbl_net_recv = QLabel('-')
        self.lbl_net_sent = QLabel('-')
        self.lbl_net_rate = QLabel('-')

        # 用于计算当前网络速率（需要和上一帧对比）
        self._last_recv = None
        self._last_sent = None
        self._last_time = None

        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        # ---- 基本信息 ----
        box_basic = QGroupBox('基本信息')
        grid_basic = QGridLayout(box_basic)
        grid_basic.addWidget(QLabel('时间:'), 0, 0)
        grid_basic.addWidget(self.lbl_time, 0, 1)
        grid_basic.addWidget(QLabel('主机名:'), 1, 0)
        grid_basic.addWidget(self.lbl_host, 1, 1)
        root.addWidget(box_basic)

        # ---- 资源使用 ----
        box_res = QGroupBox('资源使用')
        grid_res = QGridLayout(box_res)
        grid_res.addWidget(QLabel('CPU 使用率:'), 0, 0)
        grid_res.addWidget(self.lbl_cpu, 0, 1)
        grid_res.addWidget(QLabel('内存使用率:'), 1, 0)
        grid_res.addWidget(self.lbl_mem_percent, 1, 1)
        grid_res.addWidget(QLabel('内存总大小:'), 2, 0)
        grid_res.addWidget(self.lbl_mem_total, 2, 1)
        grid_res.addWidget(QLabel('剩余内存:'), 3, 0)
        grid_res.addWidget(self.lbl_mem_avail, 3, 1)
        root.addWidget(box_res)

        # ---- 网络 ----
        box_net = QGroupBox('网络')
        grid_net = QGridLayout(box_net)
        grid_net.addWidget(QLabel('累计接收:'), 0, 0)
        grid_net.addWidget(self.lbl_net_recv, 0, 1)
        grid_net.addWidget(QLabel('累计发送:'), 1, 0)
        grid_net.addWidget(self.lbl_net_sent, 1, 1)
        grid_net.addWidget(QLabel('当前速率:'), 2, 0)
        grid_net.addWidget(self.lbl_net_rate, 2, 1)
        root.addWidget(box_net)

    def update_status(self, msg: SystemStatus):
        """收到一条新消息时刷新界面。"""
        # ROS2 默认时钟为系统时间（Unix 秒），转成本地时间字符串
        t = datetime.fromtimestamp(msg.stamp.sec + msg.stamp.nanosec * 1e-9)
        self.lbl_time.setText(t.strftime('%Y-%m-%d %H:%M:%S'))

        self.lbl_host.setText(msg.hostname)
        self.lbl_cpu.setText(f'{msg.cpu_percent:.1f} %')
        self.lbl_mem_percent.setText(f'{msg.mem_percent:.1f} %')
        self.lbl_mem_total.setText(f'{msg.mem_total_mb:.1f} MB')
        self.lbl_mem_avail.setText(f'{msg.mem_available_mb:.1f} MB')
        self.lbl_net_recv.setText(fmt_bytes(msg.net_recv_bytes))
        self.lbl_net_sent.setText(fmt_bytes(msg.net_sent_bytes))

        # 计算当前网络速率（KB/s）：用两次消息的差值除以时间差
        now = t.timestamp()
        if self._last_recv is not None and self._last_time is not None:
            dt = now - self._last_time
            if dt > 0:
                recv_rate = (msg.net_recv_bytes - self._last_recv) / dt / 1024
                sent_rate = (msg.net_sent_bytes - self._last_sent) / dt / 1024
                self.lbl_net_rate.setText(
                    f'↓ {recv_rate:.1f} KB/s    ↑ {sent_rate:.1f} KB/s')
        self._last_recv = msg.net_recv_bytes
        self._last_sent = msg.net_sent_bytes
        self._last_time = now


class MonitorGuiNode(Node):
    """把 ROS2 订阅和 Qt 界面组合起来的节点。"""

    def __init__(self):
        super().__init__('system_monitor_gui')
        self.subscription = self.create_subscription(
            SystemStatus, 'system_status', self.on_status, 10)

        # Qt 应用与主窗口
        self.app = QApplication(sys.argv)
        self.window = SystemMonitorWindow()

        # 关键：用 QTimer 每 10ms 调一次 spin_once，
        # 推进 ROS2 的消息处理；回调在 Qt 主线程内执行，更新控件是安全的。
        self.timer = QTimer()
        self.timer.timeout.connect(self._spin)
        self.timer.start(10)

        self.get_logger().info('图形界面节点已启动，订阅话题: /system_status')

    def on_status(self, msg: SystemStatus):
        self.window.update_status(msg)

    def _spin(self):
        rclpy.spin_once(self, timeout_sec=0)

    def run(self):
        self.window.show()
        self.app.exec_()   # 进入 Qt 主事件循环


def main(args=None):
    rclpy.init(args=args)
    node = MonitorGuiNode()
    try:
        node.run()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
