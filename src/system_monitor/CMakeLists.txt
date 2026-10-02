cmake_minimum_required(VERSION 3.8)
project(system_monitor)

# 开启常见告警（仅在 GCC/Clang 下）
if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# 查找依赖
find_package(ament_cmake REQUIRED)
find_package(builtin_interfaces REQUIRED)
find_package(rosidl_default_generators REQUIRED)

# 生成自定义消息（会同时生成 C++ 和 Python 版本的代码）
rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/SystemStatus.msg"
  DEPENDENCIES builtin_interfaces
)

ament_export_dependencies(rosidl_default_runtime)

# 把 Python 发布节点作为可执行文件安装到 lib/system_monitor
# 安装后可通过: ros2 run system_monitor monitor_publisher.py 启动
install(PROGRAMS
  scripts/monitor_publisher.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
