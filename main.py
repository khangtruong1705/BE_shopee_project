from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware
from app.api.main import api_router
from app.core.config import settings
from sqlmodel import Session
from app.core.db import engine
import socketio
import asyncio

session = Session(engine)


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins= settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)



sio = socketio.AsyncServer(async_mode="asgi",
                           cors_allowed_origins=settings.BACKEND_CORS_ORIGINS
                           )
app_sio = socketio.ASGIApp(sio, app)



@sio.event
async def connect(sid,environ):
    print(f"Client {sid} connected")

@sio.event
async def disconnect(sid):
    print(f"Client {sid} disconnected")


@sio.event
async def join_room(sid, data):
    try:
        user_id = data.get("user_id")
        shop_id = data.get("shop_id")
        print('user_id',user_id)
        print('shop_id',shop_id)
        print('sid',sid)
        if not user_id or not shop_id:
            await sio.emit("error", {"data": "Thiếu user_id hoặc shop_id"}, to=sid)
            return

        room_id = f"user_{user_id}_to_owner_{shop_id}"
        await sio.enter_room(sid, room_id)


        await sio.emit("message", {"message": f"Đã vào phòng {room_id}"}, to=sid)

    except Exception as e:
        print("Lỗi:", e)
        await sio.emit("error", {"data": "Lỗi khi join room"}, to=sid)

@sio.event
async def client_message(sid, data):
    try:
        user_id = data.get("user_id")
        shop_id = data.get("shop_id")
        role = data.get("role")
        message = data.get("message")
        if not user_id or not shop_id or not message:
            await sio.emit("error", {"data": "Missing user_id, shop_id, or message"}, to=sid)
            return
        room_id = f"user_{user_id}_to_owner_{shop_id}"
       
        await sio.emit("server_message", {"role":role,"shop_id": shop_id,"user_id": user_id}, skip_sid=sid)
        print(f"Received message from {sid} in room {room_id}: {message}")
        
        await asyncio.sleep(0.5)
        await sio.emit("room_message", {
            "user_id": user_id,
            "shop_id": shop_id,
            "message": {
        "from": role,
        "text": message
    },
            "room":room_id
        }, room=room_id,skip_sid=sid)

    except Exception as e:
        print(f"Error handling message from {sid}: {e}")
        await sio.emit("error", {"data": "Invalid message format"}, to=sid)


