from logging import getLogger
from typing import Dict, List, Optional, Any

from pydantic import BaseModel, constr

logger = getLogger(__name__)
user_id = constr(regex=r'^[0-9]*$')


class ContactEntry(BaseModel):
    remind3d: bool = False
    remind1d: bool = False
    newevent: bool = False

    def __str__(self) -> str:
        return '\n'.join([f"{k}: {'yes' if v else 'no'}" for k, v in self._iter()])


class UserData(BaseModel):
    id: str
    user_name: str
    full_name: str
    contact: ContactEntry = ContactEntry()


class UserDataLookup(BaseModel):
    __root__: Dict[user_id, UserData] = {}

    def __iter__(self):
        return iter(self.__root__)

    def __getitem__(self, item):
        return self.__root__[item]


class UserModel(BaseModel):
    id: str
    name: str
    plus: Optional[int] = 0

    def __eq__(self, other: Any):
        t = type(other)
        if t == type(self):
            return self.id == other.id
        elif t == dict:
            return self.id == other['id']
        elif t == str:
            return self.id == other
        return False

    def __repr__(self) -> str:
        return f'UserModel(id="{self.id}", name="{self.name}")'


class UserList(BaseModel):
    __root__: List[UserModel]

    def __contains__(self, item: UserModel) -> bool:
        for i in self.__root__:
            if i.id == item.id:
                return True
        return False
