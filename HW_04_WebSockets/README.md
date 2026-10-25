# HW-04 — WebSocket новости на aiohttp

Итоговое задание модуля 54.

## Реализовано

1. Клиенты подключаются к серверу по WebSocket и получают новости без перезагрузки страницы.
2. Новая новость принимается методом `POST /news` и рассылается всем подключённым клиентам.
3. Соединение периодически проверяется сообщениями `ping` / `pong`, которые не изменяют данные. Дополнительно есть `GET /ping` для проверки доступности сервера.
4. Страница отображает полученные новости.

## Запуск

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python server.py
```

Открыть в браузере:

`http://localhost:8080/`

Можно открыть страницу сразу в нескольких вкладках.

## Отправка новости

В PowerShell:

```powershell
Invoke-RestMethod -Uri http://localhost:8080/news `
    -Method Post `
    -ContentType "application/json" `
    -Body '{"message":"Новая новость для всех клиентов"}'
```

Новость сразу появится во всех открытых вкладках.

## Проверка сервера

```powershell
Invoke-RestMethod -Uri http://localhost:8080/ping -Method Get
```

Ответ:

```json
{"status": "ok"}
```
