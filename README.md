# ROS2 系统状态监控 实践项目

用 **2 个 ROS2 包** 实现系统实时状态监控，并用 **Qt 小窗口** 实时显示。

- **包 1 `system_monitor`**（发布节点，`ament_cmake`）：定义自定义消息 `SystemStatus`，用 `psutil` 周期采集系统信息并发布。
- **包 2 `system_monitor_gui`**（订阅节点，`ament_python`）：订阅 `/system_status` 话题，用 PyQt5 小窗口显示。

---

## 一、项目结构

```
ros2_system_monitor/
├── README.md
├── test_system_info.py          # 独立测试脚本（不依赖 ROS2，先验证 psutil）
└── src/
    ├── system_monitor/          # 包1：发布 + 自定义消息
    │   ├── CMakeLists.txt
    │   ├── package.xml
    │   ├── msg/
    │   │   └── SystemStatus.msg # 自定义消息定义
    │   └── scripts/
    │       └── monitor_publisher.py
    └── system_monitor_gui/      # 包2：Qt 界面订阅
        ├── package.xml
        ├── setup.py
        ├── setup.cfg
        ├── resource/
        │   └── system_monitor_gui
        └── system_monitor_gui/
            ├── __init__.py
            └── gui_node.py
```

---

## 二、功能与消息字段

`SystemStatus.msg` 包含：

| 字段 | 含义 |
|------|------|
| `stamp` | 记录信息的时间（ROS2 时间戳） |
| `hostname` | 主机名 |
| `cpu_percent` | CPU 使用率（%） |
| `mem_percent` | 内存使用率（%） |
| `mem_total_mb` | 内存总大小（MB） |
| `mem_available_mb` | 剩余可用内存（MB） |
| `net_recv_bytes` | 网络累计接收字节数 |
| `net_sent_bytes` | 网络累计发送字节数 |

---

## 三、环境要求（在虚拟机里）

| 系统 | ROS2 发行版 | Python |
|------|-------------|--------|
| Ubuntu 20.04 | Foxy | 3.8 |
| Ubuntu 22.04 | Humble | 3.10 |
| Ubuntu 24.04 | Jazzy | 3.12 |

> 代码与发行版无关，以上三种均可。国内课程最常用 **Ubuntu 22.04 + Humble**。

---

## 四、快速开始

### 1. 安装依赖（在虚拟机里）

```bash
# psutil（采集系统信息） + PyQt5（图形界面）
sudo apt update
sudo apt install -y python3-psutil python3-pyqt5
# 或者用 pip：
# pip3 install psutil PyQt5
```

### 2. 把代码放进虚拟机

把整个 `ros2_system_monitor` 文件夹拷贝到虚拟机（共享文件夹 / 拖拽 / `scp` / Git 均可），例如放到 `~/` 下。

### 3. 编译

```bash
cd ~/ros2_system_monitor
colcon build
source install/setup.bash
```

> 以后每次新开终端运行前，都要先 `source install/setup.bash`（或写进 `~/.bashrc`）。

### 4. 运行

开两个终端，都先 `source install/setup.bash`：

```bash
# 终端 1：启动发布节点
ros2 run system_monitor monitor_publisher.py

# 终端 2：启动图形界面
ros2 run system_monitor_gui system_monitor_gui
```

界面弹出后即可看到实时刷新的系统信息。

### 5. 命令行验证（不打开界面也能看数据）

```bash
ros2 topic list                       # 应看到 /system_status
ros2 topic echo /system_status        # 直接打印消息内容
ros2 interface show system_monitor/msg/SystemStatus   # 查看消息结构
```

---

## 五、常见问题排查

| 现象 | 原因 / 解决 |
|------|------------|
| `colcon: command not found` | 没装 colcon：`sudo apt install -y python3-colcon-common-extensions` |
| `ModuleNotFoundError: psutil` | 没装 psutil：`sudo apt install -y python3-psutil` |
| `ModuleNotFoundError: PyQt5` | 没装 PyQt5：`sudo apt install -y python3-pyqt5` |
| 报 `system_monitor.msg` 找不到 | 忘了 `source install/setup.bash`，重新 source 即可 |
| 界面无法显示 | GUI 必须在有图形界面的虚拟机里运行，SSH 纯命令行环境无显示 |
| CPU 第一次显示 0.0 | 属正常，`cpu_percent` 首次调用会返回 0，代码里已做“预热” |

---

## 六、可自行扩展的方向

1. 用参数调节发布频率：`ros2 run system_monitor monitor_publisher.py --ros-args -p publish_rate:=5.0`
2. 增加磁盘使用率、进程数等字段（在 `.msg` 里加字段 + 发布端采集 + 界面加标签）。
3. 用 `rqt_graph` 查看节点/话题拓扑图。
