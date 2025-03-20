import io
import uuid
from datetime import datetime
from typing import List, Optional

import aiohttp
from app.dependencies import get_db, get_minio, get_minio_config
from app.models.digest import Digest
from app.schemas.digests import DigestCreate, DigestList, DigestResponse, DigestUpdate
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse, Response
from miniopy_async import Minio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


# TODO:
#  на бэкенде в routes надо изменить методы create_digest и update_digest.
#  надо в аргументы функций добавить summary и передавать его внутри в создание digest_data

@router.post("/", response_model=DigestResponse)
async def create_digest(
        pdf_file: UploadFile = File(...),
        title: Optional[str] = Form(None),
        body: str = Form(...),
        start_datetime: datetime = Form(...),
        end_datetime: datetime = Form(...),
        article_ids: Optional[List[str]] = Form(None),
        db: AsyncSession = Depends(get_db),
        minio: Minio = Depends(get_minio),
        # ?
        # не уверен что так правильно
        summary: str = Form(None)
):
    try:
        digest_data = DigestCreate(
            title=title,
            body=body,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            article_ids=article_ids,
            summary=summary
        )

        content = await pdf_file.read()
        file_obj = io.BytesIO(content)
        file_size = len(content)

        object_name = f"digests/{str(uuid.uuid4())}.pdf"
        bucket_name = get_minio_config()["bucket_name"]

        await minio.put_object(
            bucket_name,
            object_name,
            file_obj,
            file_size,
            content_type="application/pdf",
        )

        minio_url = f"minio://{bucket_name}/{object_name}"

        digest = Digest(
            **digest_data.model_dump(),
            s3_url=minio_url,
        )

        db.add(digest)
        await db.commit()
        await db.flush()
        await db.refresh(digest)

        return digest
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/{digest_id}")
async def download_pdf(
        digest_id: int,
        db: AsyncSession = Depends(get_db),
        minio: Minio = Depends(get_minio),
):
    # Get the digest from database
    result = await db.execute(select(Digest).where(Digest.id == digest_id))
    digest = result.scalars().first()
    if not digest:
        raise HTTPException(status_code=404, detail="Digest not found")

    try:
        # Extract bucket and object name from s3_url
        bucket_name = get_minio_config()["bucket_name"]
        object_name = digest.s3_url.split(bucket_name)[1]
        # Get the file from MinIO with async session
        async with aiohttp.ClientSession() as session:
            response = await minio.get_object(bucket_name, object_name, session)
            file_data = await response.read()
            # await response.close()
            # await response.release_conn()

        # Return as file response with proper headers
        return Response(
            content=file_data,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={object_name}",
                "Content-Length": str(len(file_data)),
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download PDF: {str(e)}")


@router.get("/{digest_id}", response_model=DigestResponse)
async def get_digest(digest_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Digest).where(Digest.id == digest_id))
    digest = result.scalars().first()
    if not digest:
        raise HTTPException(status_code=404, detail="Digest not found")
    return digest


@router.get("/", response_model=DigestList)
async def list_digests(
        skip: int = 0, limit: int = 20, db: AsyncSession = Depends(get_db)
):
    total_result = await db.execute(select(Digest))
    total = len(total_result.scalars().all())

    stmt = select(Digest).offset(skip).limit(limit)
    result = await db.execute(stmt)
    digests = result.scalars().all()

    return DigestList(items=digests, total=total, skip=skip, limit=limit)


@router.put("/{digest_id}", response_model=DigestResponse)
async def update_digest(
        digest_id: int,
        pdf_file: Optional[UploadFile] = File(None),
        title: Optional[str] = Form(None),
        body: Optional[str] = Form(None),
        start_datetime: Optional[datetime] = Form(None),
        end_datetime: Optional[datetime] = Form(None),
        article_ids: Optional[List[str]] = Form(None),
        db: AsyncSession = Depends(get_db),
        minio: Minio = Depends(get_minio),
        # ?
        # не уверен что так правильно
        summary: str = Form(None)
):
    result = await db.execute(select(Digest).where(Digest.id == digest_id))
    digest = result.scalars().first()
    if not digest:
        raise HTTPException(status_code=404, detail="Digest not found")

    try:
        update_data = DigestUpdate(
            title=title,
            body=body,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            article_ids=article_ids,
            summary=summary
        )

        if pdf_file:
            content = await pdf_file.read()
            file_obj = io.BytesIO(content)
            file_size = len(content)

            object_name = f"digests/{str(uuid.uuid4())}.pdf"
            bucket_name = get_minio_config()["bucket_name"]

            await minio.put_object(
                bucket_name,
                object_name,
                file_obj,
                file_size,
                content_type="application/pdf",
            )

            if digest.s3_url:
                old_object_name = digest.s3_url.split("/")[-1]
                try:
                    await minio.remove_object(bucket_name, old_object_name)
                except Exception:
                    pass

            digest.s3_url = f"minio://{bucket_name}/{object_name}"

        for field, value in update_data.model_dump(exclude_unset=True).items():
            setattr(digest, field, value)

        await db.commit()
        await db.flush()
        await db.refresh(digest)
        return digest
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{digest_id}")
async def delete_digest(
        digest_id: int,
        db: AsyncSession = Depends(get_db),
        minio: Minio = Depends(get_minio),
):
    result = await db.execute(select(Digest).where(Digest.id == digest_id))
    digest = result.scalars().first()
    if not digest:
        raise HTTPException(status_code=404, detail="Digest not found")

    try:
        if digest.s3_url:
            bucket_name = get_minio_config()["bucket_name"]
            object_name = digest.s3_url.split("/")[-1]
            await minio.remove_object(bucket_name, object_name)

        await db.delete(digest)
        await db.commit()
        return JSONResponse(
            status_code=200, content={"message": "Digest deleted successfully"}
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
