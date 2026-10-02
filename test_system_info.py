#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
独立测试脚本：不依赖 ROS2，单独验证 psutil 能否采集到系统信息。

用途：在正式编译 ROS2 包之前，先跑一遍确认 psutil 安装正确、能取到数据，
      输出内容与发布节点采集的字段一一对应，方便排查问题。

用法（在虚拟机里）：  python3 test_system_info.py
"""
import socket
from datetime import datetime

import psutil


def fmt_bytes(n):
    """把字节数格式化成易读的 B/KB/MB/GB 字符串。"""
    value = float(n)
    for unit in ('B', 'KB', 'MB', 'GB', 'TB'):
        if value < 1024.0 or unit == 'TB':
            return f'{value:.2f} {unit}'
        value /= 1024.0
    return f'{value:.2f} TB'


def main():
    print('=== 系统信息采集测试（psutil） ===')
    print('时间:   ', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print('主机名: ', socket.gethostname())

    # CPU 使用率需要先“预热”一次，否则第一次返回 0.0
    psutil.cpu_percent(interval=None)
    print('CPU 使用率:  {:.1f} %'.format(psutil.cpu_percent(interval=None)))

    mem = psutil.virtual_memory()
    print('内存使用率:  {:.1f} %'.format(mem.percent))
    print('内存总大小:  {:.1f} MB'.format(mem.total / (1024 * 1024)))
    print('剩余内存:    {:.1f} MB'.format(mem.available / (1024 * 1024)))

    net = psutil.net_io_counters()
    print('累计接收:    ', fmt_bytes(net.bytes_recv))
    print('累计发送:    ', fmt_bytes(net.bytes_sent))


if __name__ == '__main__':
    main()
