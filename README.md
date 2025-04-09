# SearchAPI MCP Server

这是一个基于 FastMCP 框架的搜索 API 服务器，提供了对 Google Maps、Google Flights、Google Hotels 等服务的访问接口。

## 功能特性

- Google Maps 搜索和地点信息查询
- Google Flights 航班搜索和价格比较
- Google Hotels 酒店搜索和预订信息
- Google Maps Reviews 评论数据获取

## 安装说明

1. 克隆仓库：
```bash
git clone [repository-url]
cd searchapi
```

2. 创建并激活虚拟环境：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate  # Windows
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 配置环境变量：
```bash
cp .env.example .env
```
然后编辑 `.env` 文件，填入您的 SearchAPI.io API 密钥。

## 使用方法

1. 启动服务器：
```bash
python mcp_server.py
```

2. 服务器将在默认端口启动，您可以通过 FastMCP 客户端调用相应的工具函数。

## API 说明

### Google Maps 搜索
```python
search_google_maps(query: str, location_ll: str = None)
```

### Google Flights 搜索
```python
search_google_flights(
    departure_id: str,
    arrival_id: str,
    outbound_date: str,
    flight_type: str = "round_trip",
    return_date: str = None,
    ...
)
```

### Google Hotels 搜索
```python
search_google_hotels(
    q: str,
    check_in_date: str,
    check_out_date: str,
    ...
)
```

### Google Maps Reviews 搜索
```python
search_google_maps_reviews(
    place_id: str = None,
    data_id: str = None,
    ...
)
```

## 注意事项

- 请确保在使用前已经获取了 SearchAPI.io 的 API 密钥
- API 调用受到 SearchAPI.io 的使用限制和定价政策约束
- 建议在生产环境中使用适当的错误处理和重试机制

## 许可证

[您的许可证信息] 