import random
import json
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
import httpx

app = FastAPI(title="API Gateway")

# Load config (P percentage routing)
with open("config.json") as f:
    config = json.load(f)

P = config["userRoutingPercentage"]
url_v1 = config["services"]["userV1"]
url_v2 = config["services"]["userV2"]
url_order = config["services"]["order"]

client = httpx.AsyncClient()

def choose_user_service():
    return url_v1 if random.random() * 100 < P else url_v2


@app.api_route("/users", methods=["GET", "POST"])
async def users_root(request: Request):
    target = choose_user_service()
    print(f"Routing root /users request to: {target}")

    body = await request.body()

    response = await client.request(
        method=request.method,
        url=f"{target}/users",
        content=body,
        headers=request.headers
    )

    try:
        return JSONResponse(content=response.json(), status_code=response.status_code)
    except:
        return Response(content=response.text, status_code=response.status_code)


@app.api_route("/users/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def user_proxy(path: str, request: Request):
    target = choose_user_service()
    print(f"Routing /users request to: {target}")

    body = await request.body()

    response = await client.request(
        method=request.method,
        url=f"{target}/users/{path}",
        content=body,
        headers=request.headers
    )

    try:
        return JSONResponse(content=response.json(), status_code=response.status_code)
    except:
        return Response(content=response.text, status_code=response.status_code)


@app.api_route("/orders", methods=["GET", "POST"])
async def order_root(request: Request):
    body = await request.body()

    response = await client.request(
        method=request.method,
        url=f"{url_order}/orders",
        content=body,
        headers=request.headers
    )

    try:
        return JSONResponse(content=response.json(), status_code=response.status_code)
    except:
        return Response(content=response.text, status_code=response.status_code)


@app.api_route("/orders/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def order_proxy(path: str, request: Request):
    body = await request.body()

    response = await client.request(
        method=request.method,
        url=f"{url_order}/orders/{path}",
        content=body,
        headers=request.headers
    )

    try:
        return JSONResponse(content=response.json(), status_code=response.status_code)
    except:
        return Response(content=response.text, status_code=response.status_code)
