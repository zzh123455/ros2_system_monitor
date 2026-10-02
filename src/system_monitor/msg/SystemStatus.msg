# 系统状态消息：由 system_monitor 包发布，system_monitor_gui 包订阅并显示

# 记录信息的时间（ROS2 时间戳，sec 为 Unix 秒、nanosec 为纳秒）
builtin_interfaces/Time stamp

# 主机名
string hostname

# CPU 使用率（百分比 0~100）
float32 cpu_percent

# 内存使用率（百分比 0~100）
float32 mem_percent

# 内存总大小（单位 MB）
float64 mem_total_mb

# 剩余可用内存（单位 MB）
float64 mem_available_mb

# 网络累计接收字节数（自开机以来的累计值）
uint64 net_recv_bytes

# 网络累计发送字节数（自开机以来的累计值）
uint64 net_sent_bytes
