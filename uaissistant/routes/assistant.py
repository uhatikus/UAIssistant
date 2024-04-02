from uaissistant.assistant.models import (
    CreateAssistantParams,
    CreateThreadParams,
    ListMessageResult,
    SendMessageParams,
    UpdateAssistantParams,
    UpdateThreadParams,
)
from uaissistant.assistant.service import IAssistantService
from fastapi import APIRouter, HTTPException
from fastapi_injector import Injected

router = APIRouter(prefix="/assistants", tags=["assistants"])


# GET requests
@router.get("")
async def list_assistants(
    ass: IAssistantService = Injected(IAssistantService),
):
    result = await ass.list_assistants()
    print(result)
    return result


@router.get("/{assistant_id}/threads")
async def list_threads(
    assistant_id: str,
    ass: IAssistantService = Injected(IAssistantService),
):
    result = await ass.list_threads(assistant_id)
    return result


@router.get("/{assistant_id}/threads/{thread_id}/messages")
async def list_messages(
    thread_id: str,
    ass: IAssistantService = Injected(IAssistantService),
) -> ListMessageResult:
    result = await ass.list_messages(thread_id)
    return result


# POST requests
@router.post("")
async def create_assistant(
    params: CreateAssistantParams,
    ass: IAssistantService = Injected(IAssistantService),
):
    result = await ass.create_assistant(params)
    if result.assistant.id is None:
        raise HTTPException(status_code=500, detail="Assistant creation failed")
    return result


@router.post("/{assistant_id}/threads")
async def create_thread(
    assistant_id: str,
    params: CreateThreadParams,
    ass: IAssistantService = Injected(IAssistantService),
):
    result = await ass.create_thread(assistant_id, params)
    if result.thread.id is None:
        raise HTTPException(status_code=500, detail="Thread creation failed")
    return result


@router.post("/{assistant_id}/threads/{thread_id}/messages")
async def send_message(
    assistant_id: str,
    thread_id: str,
    params: SendMessageParams,
    ass: IAssistantService = Injected(IAssistantService),
):
    result = await ass.post_thread_message(assistant_id, thread_id, params)
    return result


# DELETE requests
@router.delete("/{assistant_id}")
async def delete_assistant(
    assistant_id: str,
    ass: IAssistantService = Injected(IAssistantService),
):
    return await ass.delete_assistant(assistant_id)


@router.delete("/{assistant_id}/threads/{thread_id}")
async def delete_thread(
    assistant_id: str,
    thread_id: str,
    ass: IAssistantService = Injected(IAssistantService),
):
    return await ass.delete_thread(
        assistant_id=assistant_id, thread_id=thread_id
    )


# PATCH requests
@router.patch("/{assistant_id}")
async def update_assistant(
    assistant_id: str,
    params: UpdateAssistantParams,
    ass: IAssistantService = Injected(IAssistantService),
):
    return await ass.update_assistant(assistant_id, params)


@router.patch("/{assistant_id}/threads/{thread_id}")
async def update_thread(
    thread_id: str,
    params: UpdateThreadParams,
    ass: IAssistantService = Injected(IAssistantService),
):
    return await ass.update_thread(thread_id, params)
