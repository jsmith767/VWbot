from __future__ import annotations

from datetime import datetime
from enum import Enum
from logging import getLogger
from typing import List, Union, Protocol
from typing import Optional, Dict, Any

from pydantic import BaseModel
from telegram.ext import ContextTypes

from EmberEventBot.exceptions import EventIdError
from EmberEventBot.google_calendar import get_service, get_creds
from EmberEventBot.helpers import event_idx, star
from EmberEventBot.models.user import UserModel
from EmberEventBot.settings import EmberEventBotSettings

settings = EmberEventBotSettings()

logger = getLogger(__name__)

QUEUES = ["going", "fomo", "maybe", "waitlist"]
GOING = {"src": ["fomo", "maybe", "waitlist"], "tgt": "going"}
MAYBE = {"src": ["going", "fomo", "waitlist"], "tgt": "maybe"}
FOMO = {"src": ["going", "maybe", "waitlist"], "tgt": "fomo"}
WAITLIST = {"src": ["going", "fomo", "maybe"], "tgt": "waitlist"}
REMOVE = {"src": QUEUES, "tgt": None}


class RsvpStatus(Enum):
    GOING = "going"
    MAYBE = "maybe"
    FOMO = "fomo"
    WAITLIST = "waitlist"
    REMOVE = "remove"


class EventModel(BaseModel):
    id: str
    summary: str
    description: str = ""
    date: str
    maxhead: int
    chat: Optional[str] = None
    going: List[UserModel] = []
    waitlist: List[UserModel] = []
    maybe: List[UserModel] = []
    fomo: List[UserModel] = []
    google_event_id: Optional[str] = None
    location: Optional[str] = None

    def __str__(self):
        def plus(n: int) -> str:
            return {1: " +1", 2: " +2"}.get(n, "")

        queues = {
            "Going": "".join([f"  {x.name}{plus(x.plus)}\n" for x in self.going]),
            "Waitlist": "".join([f"  {x.name}{plus(x.plus)}\n" for x in self.waitlist]),
            "Maybe": "".join([f"  {x.name}{plus(x.plus)}\n" for x in self.maybe]),
            "FOMO": "".join([f"  {x.name}\n" for x in self.fomo]),
        }
        # noinspection PyBroadException
        try:
            d = self.get_fdate()
        except Exception as _:
            d = self.date
        msg = f"{self.id}\n{d}\n{self.summary}\n{self.description}\n"
        going = self.get_headcount('going') + self.get_headcount('maybe')
        msg += f"<b>({going}/{star(self.maxhead)})</b>\n"
        for k in queues.keys():
            headcount = self.get_headcount(k.lower())
            if headcount:
                msg += f"{k} ({headcount})\n{queues[k]}"
        return msg

    def get_headcount(self, status: str = "going") -> int:
        """Counts people that rsvpd as status and +1"""
        return sum([1 + u.plus for u in getattr(self, status)])

    def has_room(self, ppl: int = 1) -> bool:
        """Returns true if there is room to add ppl to going or maybe"""
        if self.maxhead == 0 or (
                self.get_headcount('going') +
                self.get_headcount('maybe') +
                ppl) <= self.maxhead:
            return True
        return False

    def to_dict(self) -> Dict[str, Any]:
        # noinspection LongLine
        return {
            **({"summary": self.id} if self.id is not None else {}),
            **({"location": self.location} if self.location is not None else {}),
            **({"description": self.description} if self.description is not None else {}),
            "start": {"date": datetime.strptime(self.date, settings.date_ymd).strftime("%Y-%m-%d"),
                      "timeZone": "America/Los_Angeles"},
            "end": {"date": datetime.strptime(self.date, settings.date_ymd).strftime("%Y-%m-%d"),
                    "timeZone": "America/Los_Angeles"},
            **({"google_event_id": self.google_event_id} if self.google_event_id is not None else {}),
            # "start": {"dateTime": datetime.strptime(self.date, settings.date_ymd).strftime("%Y-%m-%dT00:00:00"), "timeZone": "America/Los_Angeles"},
            # "end": {"dateTime": datetime.strptime(self.date, settings.date_ymd).strftime("%Y-%m-%dT1:00:00"), "timeZone": "America/Los_Angeles"},
        }

    def get_fdate(self) -> str:
        """returns a human friendly date."""
        return self.get_date().strftime(settings.date_long)

    def get_date(self) -> datetime:
        return datetime.strptime(self.date, settings.date_ymd)

    def commit(self, context: ContextTypes.DEFAULT_TYPE, commit_store: bool = True,
               commit_google_cal: bool = True) -> None:
        """
        Commits this calendar event to the provided calendar. If the event does not exist, creates it.
        If it already exists, edits it.
        """

        if commit_google_cal:
            if len(settings.google_cal_ember_calendar_id) == 0:
                logger.error("Event not persisted to Google Calendar. No Calendar ID set.")
                return
            try:
                creds = get_creds()
                service = get_service(creds)
                if self.google_event_id is None:
                    event = service.events().insert(calendarId=settings.google_cal_ember_calendar_id,
                                                    body=self.to_dict()).execute()
                    self.google_event_id = event.get("id")
                else:
                    service.events().update(calendarId=settings.google_cal_ember_calendar_id,
                                            eventId=self.google_event_id, body=self.to_dict()).execute()
            except Exception as e:
                logger.error(f"Error while trying to commit event to Google Calendar. Event not committed. {e}")

        if commit_store:
            try:
                idx = event_idx(self.id, context.bot_data['events']['active'])
                context.bot_data['events']['active'][idx] = self.dict()
            except EventIdError as _:
                context.bot_data['events']['active'].append(self.dict())

    def user_status(self, user: UserModel) -> str:
        """Returns the user's status for the event"""
        for i in ["going", "fomo", "maybe", "waitlist"]:
            if user in getattr(self, i):
                return i

    def mv_user(self, usr: UserModel, src: List[str], tgt: str = None):
        """Move a user from one list to another"""
        for queue in [getattr(self, x) for x in src]:
            for idx, x in enumerate(queue):
                if usr == x:
                    queue.pop(idx)
        if tgt is not None and usr not in getattr(self, tgt):
            getattr(self, tgt).append(usr)

    def set_going(self, user: UserModel) -> str:
        """Adds user to the going queue and removes them from all others"""
        curr_status = self.user_status(user)
        msg = ""
        if self.has_room() or curr_status == "maybe":  # check if the event is full
            self.mv_user(usr=user, **GOING)
            msg += f"You are listed as going for {self.id}"
            if self.chat is not None:
                msg += f"\nThe event has a side chat here: {self.chat}"
        else:
            msg += f"{self.id} is full but you can join the waitlist with /rsvpwaitlist"
        return msg

    def set_maybe(self, user: UserModel) -> str:
        """Adds user to the maybe queue and removes them from all others"""
        curr_status = self.user_status(user)
        if self.has_room() or curr_status == "going":
            self.mv_user(usr=user, **MAYBE)
            return f"You are listed as maybe for {self.id}"
        else:
            return f"{self.id} is full but you can join the waitlist with /rsvpwaitlist"

    def set_fomo(self, user: UserModel) -> str:
        """Adds user to the fomo queue and removes them from all others"""
        self.mv_user(usr=user, **FOMO)
        return f"You are listed as fomo for {self.id}"

    def set_waitlist(self, user: UserModel) -> str:
        """Adds user to the waitlist queue and removes them from all others"""
        self.mv_user(usr=user, **WAITLIST)
        return f"You are listed as waitlist for {self.id}"

    def remove_user(self, user: UserModel) -> str:
        """Removes user from all queues"""
        self.mv_user(usr=user, **REMOVE)
        return f"You have been removed from {self.id}"

    # def set_plusone(self, user: UserModel, plus) -> str:
    #     """Sets the user's plus 1 count"""
    #     pass

    def update_rsvp(self, user: UserModel, rsvp_status: str) -> str:
        """Update rsvp status after user input"""
        func = staticmethod(rsvp_map[RsvpStatus(rsvp_status)])
        msg = func(self, user=user)
        return msg

    def commit_event(self, context: ContextTypes.DEFAULT_TYPE) -> None:
        idx = event_idx(self.id, context.bot_data['events']['active'])
        for x in QUEUES:
            queue = context.bot_data['events']['active'][idx][x]
            if queue != getattr(self, x):
                d = [x.dict() for x in getattr(self, x)]
                context.bot_data['events']['active'][idx][x] = d
        pass

    def get_desc(self) -> str:
        """returns a brief event description"""
        d = datetime.strptime(self.date, '%Y%m%d').strftime(settings.date_short)
        hc = f"({self.get_headcount('going') + self.get_headcount('maybe')}/{star(self.maxhead)})"
        return f"{d} {self.id} <b>{hc}</b>: {self.summary}"


class EventList(BaseModel):
    __root__: List[EventModel]

    def __str__(self):
        self.__root__.sort(key=lambda x: x.date)
        return "".join(
            [f"{e.get_desc()}\n\n" for e in self.__root__]
        )

    def index(self, event_id: str) -> Union[int, None]:
        """Looks up the position of an event by event id"""
        for i in range(len(self.__root__)):
            if self.__root__[i].id == event_id:
                return i
        return None

    def get_user_status(self, user: UserModel) -> Dict:
        """Looks up which events a user has rsvpd for."""
        resp = {}
        for event in self.__root__:
            status = event.user_status(user=user)
            if status not in resp.keys():
                resp[status] = [event.id]
            else:
                resp[status].append(event.id)
        return resp


class SetEventStatus(Protocol):
    def __call__(self, user: UserModel) -> str: ...


rsvp_map: Dict[RsvpStatus, SetEventStatus] = {
    RsvpStatus.GOING: EventModel.set_going,
    RsvpStatus.MAYBE: EventModel.set_maybe,
    RsvpStatus.FOMO: EventModel.set_fomo,
    RsvpStatus.WAITLIST: EventModel.set_waitlist,
    RsvpStatus.REMOVE: EventModel.remove_user,
}
