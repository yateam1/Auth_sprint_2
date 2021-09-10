from abc import ABC, abstractmethod
from uuid import UUID

from app.db import db


class AbstractService(ABC):

    @property
    @abstractmethod
    def model(self) -> db.Model:
        pass

    def get_all(self):
        return self.model.query.all()

    def get_by_pk(self, pk: UUID):
        return self.model.query.filter_by(id=pk).first()

    def create(self, **kwargs):
        data = self.model.filter_kwargs(data=kwargs, exclude=['id', 'created', 'updated'])
        instance = self.model(**data)
        db.session.add(instance)
        db.session.commit()
        return instance

    def update(self, instance, **kwargs):
        data = self.model.filter_kwargs(data=kwargs, exclude=['id', 'created', 'updated'])
        for k, v in data.items():
            setattr(instance, k, v)
        db.session.commit()
        return instance

    def delete(self, instance):
        db.session.delete(instance)
        db.session.commit()
        return instance
