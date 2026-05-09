from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect
)

from backend.app.voice.websocket_manager import (
    manager
)

from backend.app.voice.speech_to_text import (
    transcribe_audio
)

router = APIRouter()


@router.websocket("/ws")
async def realtime_websocket(
    websocket: WebSocket
):

    await manager.connect(
        websocket
    )

    try:

        while True:

            data = await websocket.receive_bytes()

            transcript = await transcribe_audio(
                data
            )

            await websocket.send_json(
                {
                    "type": "transcript",
                    "text": transcript
                }
            )

    except WebSocketDisconnect:

        manager.disconnect(
            websocket
        )

    except Exception as e:

        await websocket.send_json(
            {
                "type": "error",
                "message": str(e)
            }
        )

        manager.disconnect(
            websocket
        )