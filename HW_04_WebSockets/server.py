from pathlib import Path

from aiohttp import WSMsgType, web


BASE_DIR = Path(__file__).resolve().parent
HTML_FILE = BASE_DIR / "websocket.html"


async def index(request: web.Request):
    """Отдаёт страницу или открывает WebSocket-соединение."""
    ws = web.WebSocketResponse()
    can_prepare = ws.can_prepare(request)

    if not can_prepare.ok:
        return web.FileResponse(HTML_FILE)

    await ws.prepare(request)
    request.app["sockets"].add(ws)

    await ws.send_str("Соединение установлено")

    try:
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                # Сообщение ping ничего не меняет, а только проверяет соединение.
                if msg.data == "ping":
                    await ws.send_str("pong")
            elif msg.type == WSMsgType.ERROR:
                print("WebSocket error:", ws.exception())
    finally:
        request.app["sockets"].discard(ws)

    return ws


async def add_news(request: web.Request):
    """Получает новую новость методом POST /news и рассылает клиентам."""
    try:
        data = await request.json()
    except Exception:
        return web.json_response(
            {"error": "Отправьте JSON вида: {\"message\": \"Текст новости\"}"},
            status=400,
        )

    message = data.get("message")
    if not isinstance(message, str) or not message.strip():
        return web.json_response(
            {"error": "Поле message обязательно и не должно быть пустым"},
            status=400,
        )

    message = message.strip()
    disconnected = []

    for ws in request.app["sockets"]:
        if ws.closed:
            disconnected.append(ws)
            continue
        await ws.send_str(message)

    for ws in disconnected:
        request.app["sockets"].discard(ws)

    return web.json_response(
        {
            "status": "ok",
            "message": message,
            "clients": len(request.app["sockets"]),
        }
    )


async def ping(request: web.Request):
    """GET-запрос для проверки доступности сервера. Ничего не изменяет."""
    return web.json_response({"status": "ok"})


async def on_shutdown(app: web.Application):
    for ws in list(app["sockets"]):
        await ws.close(code=1001, message=b"Server shutdown")


def init() -> web.Application:
    app = web.Application()
    app["sockets"] = set()

    app.router.add_get("/", index)
    app.router.add_post("/news", add_news)
    app.router.add_get("/ping", ping)

    app.on_shutdown.append(on_shutdown)
    return app


if __name__ == "__main__":
    web.run_app(init(), host="localhost", port=8080)
