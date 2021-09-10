from datetime import datetime
from typing import Iterable, Optional
from uuid import uuid4

from sqlalchemy import inspect
from sqlalchemy.dialects.postgresql import UUID

from app.db import db


class TimestampWithUUIDMixin:
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated = db.Column(db.DateTime, onupdate=datetime.utcnow)


class InspectFieldsMixin:

    @classmethod
    def fields_name(cls) -> set:
        """Возвращает список полей модели."""
        mapper = inspect(cls)
        return {column.key for column in mapper.attrs}

    @classmethod
    def filter_kwargs(cls, data: dict, exclude: Optional[Iterable] = None,):
        """Оставляет только те ключи, которые есть в полях модели."""
        fields = cls.fields_name()
        if exclude:
            fields -= set(exclude)
        return {k: v for k, v in data.items() if k in fields}


class BaseModel(TimestampWithUUIDMixin, InspectFieldsMixin):
    pass
