# SearchAPI MCP Server

一个基于 Model Context Protocol (MCP) 的搜索 API 服务器，提供了对 Google Maps、Google Flights、Google Hotels 等服务的标准化访问接口。该服务器使 AI 助手能够通过统一的接口访问各种搜索服务。

A Model Context Protocol (MCP) based search API server that provides standardized access to Google Maps, Google Flights, Google Hotels and other services. This server enables AI assistants to access various search services through a unified interface.

## 概述 | Overview

SearchAPI-MCP-Server 实现了 Model Context Protocol，将各种搜索操作封装为工具和资源。它作为 AI 助手和搜索服务之间的桥梁，支持地图搜索、航班查询、酒店预订等多种功能。

SearchAPI-MCP-Server implements the Model Context Protocol, encapsulating various search operations as tools and resources. It serves as a bridge between AI assistants and search services, supporting map search, flight queries, hotel bookings, and more.

## 功能特性 | Features

### Google 搜索 | Google Search
* 网页搜索结果 | Web search results
* 知识图谱集成 | Knowledge graph integration
* 相关问题推荐 | Related questions
* 搜索建议 | Search suggestions
* 多语言支持 | Multi-language support
* 地区特定结果 | Region-specific results
* 时间范围过滤 | Time range filtering
* 安全搜索选项 | Safe search options

### Google Video 搜索 | Google Video Search
* 视频内容搜索 | Video content search
* 视频列表获取 | Video list retrieval
* 视频轮播支持 | Video carousel support
* 短视频内容 | Short video content
* 按时长筛选 | Duration filtering
* 按来源过滤 | Source filtering
* 按上传时间排序 | Upload time sorting
* 高清预览支持 | HD preview support

### Google Maps 搜索 | Google Maps Search
* 搜索地点和服务 | Search places and services
* 获取地点详细信息 | Get place details
* 查看用户评论 | View user reviews
* 获取位置坐标 | Get location coordinates

### Google Flights 航班搜索 | Google Flights Search
* 单程/往返航班搜索 | One-way/round-trip flight search
* 多城市行程规划 | Multi-city itinerary planning
* 航班价格日历 | Flight price calendar
* 航班筛选和排序 | Flight filtering and sorting
* 行李额度查询 | Baggage allowance query
* 航空公司选择 | Airline selection

### Google Hotels 酒店搜索 | Google Hotels Search
* 酒店位置搜索 | Hotel location search
* 价格和可用性查询 | Price and availability query
* 设施和服务筛选 | Facilities and services filtering
* 用户评分和评论 | User ratings and reviews
* 特殊优惠查询 | Special offers query

* 房型选择 | Room type selection

### SearchAPI 新增功能 | Additional SearchAPI Features
* SearchAPI Dashboard 与账号信息 | Dashboard and account management
* 搜索历史记录查看 | View search history
* 更多搜索引擎支持，如 Google Ads Transparency、Google Shopping、Google Images、Google News、Bing、Baidu、Naver、Yahoo、Amazon、Shein、eBay、Google Play Store、Apple App Store、DuckDuckGo、YouTube
* 专用接口：Google Travel Explore、Google Hotels Autocomplete、Google Flights Location Search、Google Maps Photos、Google Maps Reviews、Google Maps Place

## 安装说明 | Installation

### 环境要求 | Requirements
* Python 3.7 或更高版本 | Python 3.7 or higher
* pip 包管理器 | pip package manager

### 基础安装 | Basic Installation

```bash
# 克隆仓库 | Clone repository
git clone https://github.com/RmMargt/searchAPI-mcp.git
cd searchAPI-mcp

# 创建并激活虚拟环境 | Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 | or
.\venv\Scripts\activate  # Windows

# 安装依赖 | Install dependencies
pip install -r requirements.txt
```

## MCP 配置 | MCP Configuration

### Claude for Desktop 配置示例 | Claude for Desktop Configuration Example

在 Claude for Desktop 的配置文件中添加以下内容：
Add the following to your Claude for Desktop configuration file:

```json
{
  "mcpServers": {
    "searchapi": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "mcp[cli]",
        "/path/to/searchAPI-mcp/mcp_server.py"
      ],
      "env": {
        "SEARCHAPI_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

配置文件位置 | Configuration file location:
* macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
* Windows: `%APPDATA%\Claude\claude_desktop_config.json`

## 许可证 | License

本项目采用 MIT 许可证 - 详见 LICENSE 文件
This project is licensed under the MIT License - see the LICENSE file for details

## 致谢 | Acknowledgments

* Model Context Protocol - 协议规范 | Protocol specification
* FastMCP - Python MCP 实现 | Python MCP implementation
* SearchAPI.io - 搜索服务提供商 | Search service provider

---

_注意：本服务器会与外部 API 进行交互。在使用 MCP 客户端确认操作之前，请始终验证请求的操作是否合适。_
_Note: This server interacts with external APIs. Always verify that requested operations are appropriate before confirming them in MCP clients._ 