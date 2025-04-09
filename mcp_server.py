# 建议将此代码保存为 mcp_server.py

import os
from typing import Any, Dict, List, Optional
import httpx
from mcp.server.fastmcp import FastMCP
from datetime import datetime, timedelta

# 从环境变量中读取 API Key，更安全
SEARCHAPI_API_KEY = os.environ.get("SEARCHAPI_API_KEY") # 重要：运行前请设置环境变量 SEARCHAPI_API_KEY

if not SEARCHAPI_API_KEY:
    print("错误：请设置环境变量 SEARCHAPI_API_KEY")
    # exit(1) # 如果希望在API Key缺失时阻止服务器启动，可以取消此注释

# 初始化 FastMCP 服务器
mcp = FastMCP("searchapi")

# 常量
SEARCHAPI_URL = "https://www.searchapi.io/api/v1/search"

async def make_searchapi_request(params: Dict[str, Any]) -> Dict[str, Any]:
    """向searchapi.io发送请求并处理错误情况"""
    # 确保API Key被添加到参数中
    params["api_key"] = SEARCHAPI_API_KEY
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(SEARCHAPI_URL, params=params, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            error_detail = None
            try:
                if hasattr(e, 'response') and e.response:
                    error_detail = e.response.json()
            except ValueError:
                if hasattr(e, 'response') and e.response:
                    error_detail = e.response.text
            
            error_message = f"调用searchapi.io时出错: {e}"
            if error_detail:
                error_message += f", 详情: {error_detail}"
            
            return {"error": error_message}
        except Exception as e:
            return {"error": f"处理请求时发生未知错误: {e}"}

@mcp.tool()
async def search_google_maps(query: str, location_ll: str = None) -> Dict[str, Any]:
    """搜索Google地图上的地点或服务"""
    params = {
        "engine": "google_maps",
        "q": query
    }
    
    if location_ll:
        params["ll"] = location_ll
    
    return await make_searchapi_request(params)

@mcp.tool()
async def search_google_flights(
    departure_id: str, 
    arrival_id: str, 
    outbound_date: str, 
    flight_type: str = "round_trip", 
    return_date: str = None,
    gl: str = None,
    hl: str = None,
    currency: str = None,
    travel_class: str = None,
    stops: str = None,
    sort_by: str = None,
    adults: str = None,
    children: str = None,
    multi_city_json: str = None,
    show_cheapest_flights: str = None,
    show_hidden_flights: str = None,
    max_price: str = None,
    carry_on_bags: str = None,
    checked_bags: str = None,
    included_airlines: str = None,
    excluded_airlines: str = None,
    outbound_times: str = None,
    return_times: str = None,
    emissions: str = None,
    included_connecting_airports: str = None,
    excluded_connecting_airports: str = None,
    layover_duration_min: str = None,
    layover_duration_max: str = None,
    max_flight_duration: str = None,
    separate_tickets: str = None,
    infants_in_seat: str = None,
    infants_on_lap: str = None,
    departure_token: str = None,
    booking_token: str = None
) -> Dict[str, Any]:
    """搜索Google航班信息"""
    params = {
        "engine": "google_flights",
        "flight_type": flight_type
    }
    
    # 处理flight_type不同情况下的必填参数
    if flight_type == "multi_city":
        if not multi_city_json:
            return {"error": "多城市行程需要'multi_city_json'参数"}
        params["multi_city_json"] = multi_city_json
    else:
        params["departure_id"] = departure_id
        params["arrival_id"] = arrival_id
        params["outbound_date"] = outbound_date
        
        if flight_type == "round_trip":
            if not return_date:
                return {"error": "往返行程需要'return_date'参数"}
            params["return_date"] = return_date
    
    # 添加可选参数
    optional_params = {
        "gl": gl,
        "hl": hl,
        "currency": currency,
        "travel_class": travel_class,
        "stops": stops,
        "sort_by": sort_by,
        "adults": adults,
        "children": children,
        "show_cheapest_flights": show_cheapest_flights,
        "show_hidden_flights": show_hidden_flights,
        "max_price": max_price,
        "carry_on_bags": carry_on_bags,
        "checked_bags": checked_bags,
        "included_airlines": included_airlines,
        "excluded_airlines": excluded_airlines,
        "outbound_times": outbound_times,
        "return_times": return_times,
        "emissions": emissions,
        "included_connecting_airports": included_connecting_airports,
        "excluded_connecting_airports": excluded_connecting_airports,
        "layover_duration_min": layover_duration_min,
        "layover_duration_max": layover_duration_max,
        "max_flight_duration": max_flight_duration,
        "separate_tickets": separate_tickets,
        "infants_in_seat": infants_in_seat,
        "infants_on_lap": infants_on_lap,
        "departure_token": departure_token,
        "booking_token": booking_token
    }
    
    # 添加有值的可选参数
    for key, value in optional_params.items():
        if value is not None:
            params[key] = value
    
    return await make_searchapi_request(params)

@mcp.tool()
async def search_google_hotels(
    q: str, 
    check_in_date: str, 
    check_out_date: str,
    gl: str = None,
    hl: str = None,
    currency: str = None,
    property_type: str = None,
    sort_by: str = None,
    price_min: str = None,
    price_max: str = None,
    property_types: str = None,
    amenities: str = None,
    rating: str = None,
    free_cancellation: str = None,
    special_offers: str = None,
    for_displaced_individuals: str = None,
    eco_certified: str = None,
    hotel_class: str = None,
    brands: str = None,
    bedrooms: str = None,
    bathrooms: str = None,
    adults: str = None,
    children_ages: str = None,
    next_page_token: str = None
) -> Dict[str, Any]:
    """搜索Google酒店信息"""
    params = {
        "engine": "google_hotels",
        "q": q,
        "check_in_date": check_in_date,
        "check_out_date": check_out_date
    }
    
    # 添加可选参数
    optional_params = {
        "gl": gl,
        "hl": hl,
        "currency": currency,
        "property_type": property_type,
        "sort_by": sort_by,
        "price_min": price_min,
        "price_max": price_max,
        "property_types": property_types,
        "amenities": amenities,
        "rating": rating,
        "free_cancellation": free_cancellation,
        "special_offers": special_offers,
        "for_displaced_individuals": for_displaced_individuals,
        "eco_certified": eco_certified,
        "hotel_class": hotel_class,
        "brands": brands,
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
        "adults": adults,
        "children_ages": children_ages,
        "next_page_token": next_page_token
    }
    
    # 添加有值的可选参数
    for key, value in optional_params.items():
        if value is not None:
            params[key] = value
    
    return await make_searchapi_request(params)

@mcp.tool()
async def search_google_maps_reviews(
    place_id: str = None,
    data_id: str = None,
    topic_id: str = None,
    next_page_token: str = None,
    sort_by: str = None,
    rating: str = None,
    hl: str = None,
    gl: str = None,
    reviews_limit: str = None
) -> Dict[str, Any]:
    """搜索Google地图上的评论数据"""
    params = {
        "engine": "google_maps_reviews"
    }
    
    # 检查必填参数
    if place_id:
        params["place_id"] = place_id
    elif data_id:
        params["data_id"] = data_id
    else:
        return {"error": "必须提供place_id或data_id参数"}
    
    # 添加其他可选参数
    optional_params = {
        "topic_id": topic_id,
        "next_page_token": next_page_token,
        "sort_by": sort_by,
        "rating": rating,
        "hl": hl,
        "gl": gl,
        "reviews_limit": reviews_limit
    }
    
    # 添加有值的可选参数
    for key, value in optional_params.items():
        if value is not None:
            params[key] = value
    
    return await make_searchapi_request(params)

@mcp.tool()
async def search_google_hotels_property(
    property_token: str,
    check_in_date: str,
    check_out_date: str,
    gl: str = None,
    hl: str = None,
    currency: str = None,
    adults: str = None,
    children: str = None,
    children_ages: str = None
) -> Dict[str, Any]:
    """查询Google酒店详细信息"""
    params = {
        "engine": "google_hotels_property",
        "property_token": property_token,
        "check_in_date": check_in_date,
        "check_out_date": check_out_date
    }
    
    # 添加可选参数
    optional_params = {
        "gl": gl,
        "hl": hl,
        "currency": currency,
        "adults": adults,
        "children": children,
        "children_ages": children_ages
    }
    
    # 添加有值的可选参数
    for key, value in optional_params.items():
        if value is not None:
            params[key] = value
    
    return await make_searchapi_request(params)

@mcp.tool()
async def search_google_flights_calendar(
    flight_type: str,
    departure_id: str,
    arrival_id: str,
    outbound_date: str,
    return_date: str = None,
    outbound_date_start: str = None,
    outbound_date_end: str = None,
    return_date_start: str = None,
    return_date_end: str = None,
    gl: str = None,
    hl: str = None,
    currency: str = None,
    adults: str = None,
    children: str = None,
    travel_class: str = None,
    stops: str = None
) -> Dict[str, Any]:
    """查询Google航班日历价格"""
    params = {
        "engine": "google_flights_calendar",
        "flight_type": flight_type,
        "departure_id": departure_id,
        "arrival_id": arrival_id,
        "outbound_date": outbound_date
    }
    
    # 检查航班类型，确保提供必要参数
    if flight_type == "round_trip" and not return_date:
        return {"error": "往返航班需要提供return_date参数"}
    elif flight_type == "round_trip":
        params["return_date"] = return_date
    
    # 添加可选参数
    optional_params = {
        "outbound_date_start": outbound_date_start,
        "outbound_date_end": outbound_date_end,
        "return_date_start": return_date_start,
        "return_date_end": return_date_end,
        "gl": gl,
        "hl": hl,
        "currency": currency,
        "adults": adults,
        "children": children,
        "travel_class": travel_class,
        "stops": stops
    }
    
    # 添加有值的可选参数
    for key, value in optional_params.items():
        if value is not None:
            params[key] = value
    
    return await make_searchapi_request(params)

@mcp.tool()
async def get_current_time(
    format: str = "iso", 
    days_offset: str = "0",
    return_future_dates: str = "false",
    future_days: str = "7"
) -> Dict[str, Any]:
    """获取当前系统时间和旅行日期建议"""
    now = datetime.now()
    
    # 将字符串参数转换为对应的数据类型
    days_offset_int = int(days_offset) if days_offset is not None else 0
    return_future_dates_bool = return_future_dates.lower() == "true" if return_future_dates is not None else False
    future_days_int = int(future_days) if future_days is not None else 7
    
    target_date = now + timedelta(days=days_offset_int)
    
    result = {
        "now": {
            "iso": now.strftime("%Y-%m-%d"),
            "slash": now.strftime("%d/%m/%Y"),
            "chinese": now.strftime("%Y年%m月%d日"),
            "timestamp": int(now.timestamp()),
            "full": now.strftime("%Y-%m-%d %H:%M:%S"),
            "time": now.strftime("%H:%M:%S"),
            "weekday": now.strftime("%A"),
            "weekday_short": now.strftime("%a"),
            "year": now.year,
            "month": now.month,
            "day": now.day,
            "hour": now.hour,
            "minute": now.minute,
            "second": now.second
        },
        "target_date": {
            "iso": target_date.strftime("%Y-%m-%d"),
            "slash": target_date.strftime("%d/%m/%Y"),
            "chinese": target_date.strftime("%Y年%m月%d日"),
            "timestamp": int(target_date.timestamp()),
            "full": target_date.strftime("%Y-%m-%d %H:%M:%S"),
            "time": target_date.strftime("%H:%M:%S"),
            "weekday": target_date.strftime("%A"),
            "weekday_short": target_date.strftime("%a"),
            "year": target_date.year,
            "month": target_date.month,
            "day": target_date.day,
            "hour": target_date.hour,
            "minute": target_date.minute,
            "second": target_date.second
        }
    }
    
    # 旅行场景常用日期
    result["travel_dates"] = {
        "today": now.strftime("%Y-%m-%d"),
        "tomorrow": (now + timedelta(days=1)).strftime("%Y-%m-%d"),
        "next_week": (now + timedelta(days=7)).strftime("%Y-%m-%d"),
        "next_month": (now + timedelta(days=30)).strftime("%Y-%m-%d"),
        "weekend": (now + timedelta((5 - now.weekday()) % 7)).strftime("%Y-%m-%d"), # 下一个周五
        "weekend_end": (now + timedelta((6 - now.weekday()) % 7 + 1)).strftime("%Y-%m-%d"), # 下一个周日
    }
    
    # 对于旅行预订常用的入住-退房日期对
    result["hotel_stay_suggestions"] = [
        {
            "check_in": (now + timedelta(days=1)).strftime("%Y-%m-%d"),
            "check_out": (now + timedelta(days=3)).strftime("%Y-%m-%d"),
            "nights": 2,
            "description": "短暂周末度假"
        },
        {
            "check_in": (now + timedelta(days=1)).strftime("%Y-%m-%d"),
            "check_out": (now + timedelta(days=8)).strftime("%Y-%m-%d"),
            "nights": 7,
            "description": "一周度假"
        },
        {
            "check_in": (now + timedelta(days=30)).strftime("%Y-%m-%d"),
            "check_out": (now + timedelta(days=32)).strftime("%Y-%m-%d"),
            "nights": 2,
            "description": "下个月短暂出行"
        }
    ]
    
    # 如果需要一系列未来日期
    if return_future_dates_bool:
        future_dates = []
        for i in range(future_days_int):
            future_date = now + timedelta(days=i)
            future_dates.append({
                "iso": future_date.strftime("%Y-%m-%d"),
                "slash": future_date.strftime("%d/%m/%Y"),
                "chinese": future_date.strftime("%Y年%m月%d日"),
                "weekday": future_date.strftime("%A"),
                "weekday_short": future_date.strftime("%a"),
                "days_from_now": i
            })
        result["future_dates"] = future_dates
    
    # 使用请求的格式作为主要返回值
    if format == "iso":
        result["date"] = target_date.strftime("%Y-%m-%d")
    elif format == "slash":
        result["date"] = target_date.strftime("%d/%m/%Y")
    elif format == "chinese":
        result["date"] = target_date.strftime("%Y年%m月%d日")
    elif format == "timestamp":
        result["date"] = int(target_date.timestamp())
    elif format == "full":
        result["date"] = target_date.strftime("%Y-%m-%d %H:%M:%S")
    else:
        result["date"] = target_date.strftime("%Y-%m-%d")
    
    return result

@mcp.tool()
async def search_google(
    q: str,
    device: str = "desktop",
    location: str = None,
    uule: str = None,
    google_domain: str = "google.com",
    gl: str = "us",
    hl: str = "en",
    lr: str = None,
    cr: str = None,
    nfpr: str = "0",
    filter: str = "1",
    safe: str = "off",
    time_period: str = None,
    time_period_min: str = None,
    time_period_max: str = None,
    num: str = "10",
    page: str = "1"
) -> Dict[str, Any]:
    """搜索Google搜索结果，包括有机结果、知识图谱、回答框、相关问题、广告等"""
    params = {
        "engine": "google",
        "q": q
    }
    
    # 添加可选参数
    optional_params = {
        "device": device,
        "location": location,
        "uule": uule,
        "google_domain": google_domain,
        "gl": gl,
        "hl": hl,
        "lr": lr,
        "cr": cr,
        "nfpr": nfpr,
        "filter": filter,
        "safe": safe,
        "time_period": time_period,
        "time_period_min": time_period_min,
        "time_period_max": time_period_max,
        "num": num,
        "page": page
    }
    
    # 添加有值的可选参数
    for key, value in optional_params.items():
        if value is not None:
            params[key] = value
    
    return await make_searchapi_request(params)

@mcp.tool()
async def search_google_videos(
    q: str,
    device: str = "desktop",
    location: str = None,
    uule: str = None,
    google_domain: str = "google.com",
    gl: str = "us",
    hl: str = "en",
    lr: str = None,
    cr: str = None,
    nfpr: str = "0",
    filter: str = "1",
    safe: str = "off",
    time_period: str = None,
    time_period_min: str = None,
    time_period_max: str = None,
    num: str = "10",
    page: str = "1"
) -> Dict[str, Any]:
    """搜索Google视频结果，根据设备类型返回视频列表、视频轮播或短视频"""
    params = {
        "engine": "google_videos",
        "q": q
    }
    
    # 添加可选参数
    optional_params = {
        "device": device,
        "location": location,
        "uule": uule,
        "google_domain": google_domain,
        "gl": gl,
        "hl": hl,
        "lr": lr,
        "cr": cr,
        "nfpr": nfpr,
        "filter": filter,
        "safe": safe,
        "time_period": time_period,
        "time_period_min": time_period_min,
        "time_period_max": time_period_max,
        "num": num,
        "page": page
    }
    
    # 添加有值的可选参数
    for key, value in optional_params.items():
        if value is not None:
            params[key] = value
    
    return await make_searchapi_request(params)

if __name__ == "__main__":
    # 从环境变量获取 transport 类型，默认为 stdio
    transport = os.environ.get("MCP_TRANSPORT", "stdio")
    # 初始化并运行服务器
    mcp.run(transport=transport) 