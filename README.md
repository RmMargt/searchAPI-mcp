# SearchAPI MCP Server

一个基于 Model Context Protocol (MCP) 的搜索 API 服务器，提供了对 Google Maps、Google Flights、Google Hotels 等服务的标准化访问接口。该服务器使 AI 助手能够通过统一的接口访问各种搜索服务。

## 概述

SearchAPI-MCP-Server 实现了 Model Context Protocol，将各种搜索操作封装为工具和资源。它作为 AI 助手和搜索服务之间的桥梁，支持地图搜索、航班查询、酒店预订等多种功能。

## 功能特性

### Google Maps 搜索
* 搜索地点和服务
* 获取地点详细信息
* 查看用户评论
* 获取位置坐标

### Google Flights 航班搜索
* 单程/往返航班搜索
* 多城市行程规划
* 航班价格日历
* 航班筛选和排序
* 行李额度查询
* 航空公司选择

### Google Hotels 酒店搜索
* 酒店位置搜索
* 价格和可用性查询
* 设施和服务筛选
* 用户评分和评论
* 特殊优惠查询
* 房型选择

### 高级功能
* 多语言支持
* 货币转换
* 地理编码和反向地理编码
* 距离计算
* 自定义搜索参数

## 安装说明

### 环境要求
* Python 3.7 或更高版本
* pip 包管理器

### 基础安装

```bash
# 克隆仓库
git clone https://github.com/RmMargt/searchapi.git
cd searchapi

# 创建并激活虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，添加您的 API 密钥
```

## API 使用说明

### Google Maps 搜索
```python
search_google_maps(
    query: str,           # 搜索关键词
    location_ll: str = None  # 可选的位置坐标
)
```

### Google Flights 航班搜索
```python
search_google_flights(
    departure_id: str,    # 出发机场代码
    arrival_id: str,      # 到达机场代码
    outbound_date: str,   # 出发日期
    flight_type: str = "round_trip",  # 航班类型
    return_date: str = None,  # 返回日期（往返航班必填）
    ...
)
```

### Google Hotels 酒店搜索
```python
search_google_hotels(
    q: str,              # 搜索关键词
    check_in_date: str,  # 入住日期
    check_out_date: str, # 退房日期
    ...
)
```

### Google Maps Reviews 评论搜索
```python
search_google_maps_reviews(
    place_id: str = None,  # 地点ID
    data_id: str = None,   # 数据ID
    ...
)
```

## 常见问题

### API 限制
* 请确保遵守 SearchAPI.io 的使用限制
* 注意请求频率限制
* 关注 API 配额使用情况

### 错误处理
* 服务器会自动处理常见的 API 错误
* 提供详细的错误信息和建议
* 支持请求重试机制

### 调试
通过设置环境变量启用详细日志：
```bash
export MCP_DEBUG=1  # Linux/macOS
set MCP_DEBUG=1     # Windows
```

## 贡献指南

欢迎提交 Pull Request！

1. Fork 本仓库
2. 创建您的特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交您的修改 (`git commit -m '添加一些很棒的功能'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启一个 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详见 LICENSE 文件

## 致谢

* Model Context Protocol - 协议规范
* FastMCP - Python MCP 实现
* SearchAPI.io - 搜索服务提供商

---

_注意：本服务器会与外部 API 进行交互。在使用 MCP 客户端确认操作之前，请始终验证请求的操作是否合适。_ 