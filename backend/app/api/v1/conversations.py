from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.deps import get_db, get_current_user
from app.models.models import User, Conversation, Message
from app.schemas.schemas import ConversationCreate, ConversationResponse, ConversationSummary

router = APIRouter(prefix="/conversations", tags=["Conversations"])

@router.get("", response_model=List[ConversationSummary])
async def list_conversations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(Conversation)
        .where(Conversation.user_id == current_user.id)
        .order_by(Conversation.updated_at.desc())
    )
    result = await db.execute(stmt)
    convs = result.scalars().all()

    summaries = []
    for idx, c in enumerate(convs):
        msg_stmt = (
            select(Message)
            .where(Message.conversation_id == c.id)
            .order_by(Message.created_at.desc())
            .limit(1)
        )
        msg_res = await db.execute(msg_stmt)
        last_msg = msg_res.scalar_one_or_none()

        display_title = c.title or "Verification Session"
        if display_title in ["Visual Verification Session", "New Verification Chat", "Image Upload Session"]:
            if last_msg and last_msg.content and "objects can you identify" not in last_msg.content:
                display_title = last_msg.content[:24].strip()
                if len(last_msg.content) > 24:
                    display_title += "..."
            else:
                formatted_time = c.created_at.strftime("%b %d, %H:%M") if c.created_at else ""
                display_title = f"Verification ({formatted_time})" if formatted_time else f"Verification Session #{len(convs) - idx}"

        summaries.append(ConversationSummary(
            id=c.id,
            title=display_title,
            created_at=c.created_at,
            updated_at=c.updated_at,
            last_message=last_msg.content[:60] if last_msg else None
        ))
    return summaries


@router.post("", response_model=ConversationResponse)
async def create_conversation(
    conv_in: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    conv = Conversation(
        user_id=current_user.id,
        title=conv_in.title or "New Verification Chat"
    )
    db.add(conv)
    await db.commit()

    # Re-fetch with eager loading of messages and images
    stmt = (
        select(Conversation)
        .options(
            selectinload(Conversation.messages),
            selectinload(Conversation.images)
        )
        .where(Conversation.id == conv.id)
    )
    res = await db.execute(stmt)
    loaded_conv = res.scalar_one()
    return ConversationResponse.model_validate(loaded_conv)

@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(Conversation)
        .options(
            selectinload(Conversation.messages),
            selectinload(Conversation.images)
        )
        .where(Conversation.id == conversation_id, Conversation.user_id == current_user.id)
    )
    result = await db.execute(stmt)
    conv = result.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    
    resp = ConversationResponse.model_validate(conv)
    for m in resp.messages:
        if m.metadata_json and not m.why_this_answer:
            try:
                m.why_this_answer = WhyThisAnswerPayload.model_validate_json(m.metadata_json)
            except Exception:
                pass
    return resp

@router.patch("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: str,
    conv_in: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(Conversation)
        .options(
            selectinload(Conversation.messages),
            selectinload(Conversation.images)
        )
        .where(Conversation.id == conversation_id, Conversation.user_id == current_user.id)
    )
    result = await db.execute(stmt)
    conv = result.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    if conv_in.title:
        conv.title = conv_in.title
    await db.commit()

    res = await db.execute(stmt)
    loaded_conv = res.scalar_one()
    resp = ConversationResponse.model_validate(loaded_conv)
    for m in resp.messages:
        if m.metadata_json and not m.why_this_answer:
            try:
                m.why_this_answer = WhyThisAnswerPayload.model_validate_json(m.metadata_json)
            except Exception:
                pass
    return resp

@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Conversation).where(Conversation.id == conversation_id, Conversation.user_id == current_user.id)
    result = await db.execute(stmt)
    conv = result.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    await db.delete(conv)
    await db.commit()
    return {"message": "Conversation deleted successfully"}
