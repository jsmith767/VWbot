from typing import List, Dict
from logging import INFO
from pydantic import BaseSettings
from EmberEventBot.constants import ChatGroups, Decoration

class EmberJobSettings(BaseSettings):
    event_alert_enabled: bool = True
    event_alert_time: str = "09:01"
    event_alert_targets: List[str] = [
        ChatGroups.MAIN.value,
        ChatGroups.INFO.value,
    ]
    new_event_alert_interval: int = 120
    new_event_alert_targets: List[str] = [
        ChatGroups.MAIN.value,
        ChatGroups.INFO.value,
    ]
    summary_alert_days: List[int] = [1]
    summary_alert_enabled: bool = True
    summary_alert_time: str = "09:00"
    summary_alert_targets: List[str] = [
        ChatGroups.MAIN.value,
        ChatGroups.INFO.value,
    ]
    sweep_time: str = "03:30"
    user_event_alert_time: str = "07:30"

class EmberEventBotSettings(BaseSettings):
    embtoken: str = ""
    tz: str = "America/Los_Angeles"
    admin_group: str = ChatGroups.ADMIN.value
    user_group: str = ChatGroups.INFO.value
    valid_group: List[str] = [ChatGroups.BOTDEV.value]
    admin_status: List[str] = ['administrator', 'creator']
    user_status: List[str] = ['member', 'administrator', 'creator']
    dev_ids: List[int] = [731386198]
    hr: str = Decoration.STAR_HR.value
    bullet: str = "  * "
    date_short: str = "%m/%d"
    date_long: str = "%A the %d of %b %Y"
    date_ymd: str = "%Y%m%d"
    spam_delay: int = 3
    google_cal_refresh_token: str = ""
    google_cal_ember_calendar_id: str = ""
    google_cal_client_id: str = "698948236492-2ad0v7o1q28hm40q9eslc1jmivcntpeb.apps.googleusercontent.com"
    google_cal_project_id: str = "noble-office-194902"
    google_cal_client_secret: str = ""
    hlp: str = """User Commands
/help - this
/list - list events
/calendar - shows a small 2 month calendar
/myevents - shows active events you've rsvpd to
/contact - update your contact settings
/rsvp - rsvp as going,maybe,fomo to an event
/show <b>event_name</b> - show event
"""
    hlp_admin: str = """Guide Commands
/create - create an event
/rm <b>event_name</b> - remove an event
/sidechat - list sidechats
/deactivate - move an active event to inactive, optional event_id
/reactivate - move an inactive event to active, optional event_id
/edit - edit an active event

"""
    sidechat: str = """
👋 <a href="https://t.me/+nf-frP6PCjQ3MWZh">Ember Intros</a>: Ember member intros and bios!

⚡ <a href="https://t.me/+dgozOyu_p_lmMWNh">Ember Impromptu</a>: impromptu events and LFG

♀️ <a href="https://t.me/+J4xI966PRTs0ZDA5">Fember</a>: discuss femme related issues

♂️<a href="https://t.me/+524VmMT8GnE2Mjlh">Embros</a>: discuss masc related issues

⚤⚧️☿️ <a href="https://t.me/+yzDsPLETunM3N2Qx">nBer</a>: discuss nonbinary related issues

🌶️ Ember Spicy: Strut your stuff! Ask about being added.

"""
    editable_fields: Dict[str, str] = {
        'summary': 'Summary',
        'description': 'Description',
        'date': 'Date',
        'maxhead': 'HeadCount',
        'chat': 'EventChat'
    }
    log_path: str = "/var/log/ember/emberbot.log"
    log_max_bytes: int = 1048576
    log_backup_count: int = 20
    log_format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    log_level: int = INFO

    access_log_path: str = "/var/log/ember/access.log"
    access_log_when: str = "W0"
    access_log_format: str = '{"ts":"%(asctime)s","access":"%(access)s","user_id":"%(user_id)s","func_name":"%(func_name)s","access_type":"%(access_type)s","message":"%(message)s"}'
    access_log_level: int = INFO