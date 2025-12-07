"""
Простой MCP сервер для получения погоды (демонстрационный)
"""

import asyncio

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

# Создаем сервер
app = Server("weather-server")


# Определяем инструмент
@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="get_weather",
            description="Получает текущую погоду для указанного города",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "Название города"},
                    "units": {
                        "type": "string",
                        "description": "Единицы измерения: celsius или fahrenheit",
                        "enum": ["celsius", "fahrenheit"],
                    },
                },
                "required": ["city"],
            },
        ),
        Tool(
            name="get_forecast",
            description="Получает прогноз погоды на несколько дней",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "Название города"},
                    "days": {
                        "type": "integer",
                        "description": "Количество дней для прогноза (1-7)",
                    },
                },
                "required": ["city", "days"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "get_weather":
        city = arguments.get("city", "")
        units = arguments.get("units", "celsius")

        # Симулируем получение погоды
        temp = 22 if units == "celsius" else 72
        result = f"Погода в {city}: {temp}°{'C' if units == 'celsius' else 'F'}, облачно с прояснениями"

        return [TextContent(type="text", text=result)]

    elif name == "get_forecast":
        city = arguments.get("city", "")
        days = arguments.get("days", 3)

        # Симулируем прогноз
        forecast = f"Прогноз погоды для {city} на {days} дней:\n"
        for i in range(1, days + 1):
            forecast += f"День {i}: 20-25°C, переменная облачность\n"

        return [TextContent(type="text", text=forecast)]

    else:
        raise ValueError(f"Неизвестный инструмент: {name}")


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
