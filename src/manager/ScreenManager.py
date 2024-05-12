from pysondb.errors import IdDoesNotExistError
from typing import Dict, Optional, List, Tuple, Union

from src.model.entity.Screen import Screen
from src.manager.DatabaseManager import DatabaseManager
from src.manager.LangManager import LangManager
from src.manager.UserManager import UserManager
from src.service.ModelManager import ModelManager


class ScreenManager(ModelManager):

    TABLE_NAME = "fleet"
    TABLE_MODEL = [
        "name",
        "enabled",
        "position",
        "host",
        "port"
    ]

    def __init__(self, lang_manager: LangManager, database_manager: DatabaseManager, user_manager: UserManager):
        super().__init__(lang_manager, database_manager, user_manager)
        self._db = database_manager.open(self.TABLE_NAME, self.TABLE_MODEL)

    def hydrate_object(self, raw_screen: dict, id: Optional[str] = None) -> Screen:
        if id:
            raw_screen['id'] = id

        return Screen(**raw_screen)

    def hydrate_dict(self, raw_screens: dict) -> List[Screen]:
        return [self.hydrate_object(raw_screen, raw_id) for raw_id, raw_screen in raw_screens.items()]

    def hydrate_list(self, raw_screens: list) -> List[Screen]:
        return [self.hydrate_object(raw_screen) for raw_screen in raw_screens]

    def get(self, id: str) -> Optional[Screen]:
        try:
            return self.hydrate_object(self._db.get_by_id(id), id)
        except IdDoesNotExistError:
            return None

    def get_by(self, query) -> List[Screen]:
        return self.hydrate_dict(self._db.get_by_query(query=query))

    def get_one_by(self, query) -> Optional[Screen]:
        screens = self.hydrate_dict(self._db.get_by_query(query=query))
        if len(screens) == 1:
            return screens[0]
        elif len(screens) > 1:
            raise Error("More than one result for query")
        return None

    def get_all(self, sort: bool = False) -> List[Screen]:
        raw_screens = self._db.get_all()

        if isinstance(raw_screens, dict):
            if sort:
                return sorted(self.hydrate_dict(raw_screens), key=lambda x: x.position)
            return self.hydrate_dict(raw_screens)

        return self.hydrate_list(sorted(raw_screens, key=lambda x: x['position']) if sort else raw_screens)

    def get_enabled_screens(self) -> List[Screen]:
        return [screen for screen in self.get_all(sort=True) if screen.enabled]

    def get_disabled_screens(self) -> List[Screen]:
        return [screen for screen in self.get_all(sort=True) if not screen.enabled]

    def update_enabled(self, id: str, enabled: bool) -> None:
        self._db.update_by_id(id, {"enabled": enabled, "position": 999})
        
    def update_positions(self, positions: list) -> None:
        for screen_id, screen_position in positions.items():
            self._db.update_by_id(screen_id, {"position": screen_position})

    def update_form(self, id: str, name: str, host: str, port: int) -> None:
        self._db.update_by_id(id, {"name": name, "host": host, "port": port})

    def add_form(self, screen: Union[Screen, Dict]) -> None:
        form = screen

        if not isinstance(screen, dict):
            form = screen.to_dict()
            del form['id']

        self._db.add(form)

    def delete(self, id: str) -> None:
        self._db.delete_by_id(id)

    def to_dict(self, screens: List[Screen]) -> List[Dict]:
        return [screen.to_dict() for screen in screens]
