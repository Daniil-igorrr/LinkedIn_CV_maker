"""
Creates a Google Calendar event using a previously-authorized token.json
(run calendar_auth_setup.py once first to generate it).

Usage as a CLI:
    python create_calendar_event.py \
        --title "Interview: Bigle - SDR" \
        --start "2026-10-05T15:00:00" \
        --end "2026-10-05T15:30:00" \
        --timezone "Europe/Madrid" \
        --description "Job posting: https://...\nCompany site: https://..."

Usage from another script / the agent (preferred - no shell-escaping needed):
    from create_calendar_event import create_event
    create_event(
        title="Interview: Bigle - SDR",
        start="2026-10-05T15:00:00",
        end="2026-10-05T15:30:00",
        timezone="Europe/Madrid",
        description="Job posting: ...\nCompany site: ...\nLinkedIn: ...",
    )
"""

import argparse
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]
TOKEN_PATH = "token.json"


def get_credentials() -> Credentials:
    """Load token.json and refresh it if expired. Never prints its contents."""
    if not os.path.exists(TOKEN_PATH):
        raise RuntimeError(
            f"{TOKEN_PATH} not found. Run calendar_auth_setup.py once first."
        )

    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(TOKEN_PATH, "w", encoding="utf-8") as f:
                f.write(creds.to_json())
        else:
            raise RuntimeError(
                "token.json is invalid and has no refresh token. "
                "Delete token.json and re-run calendar_auth_setup.py."
            )

    return creds


def create_event(
    title: str,
    start: str,
    end: str,
    timezone: str,
    description: str = "",
    attendees: list[str] | None = None,
    calendar_id: str = "primary",
) -> dict:
    """
    start / end: ISO 8601 local time, e.g. "2026-10-05T15:00:00"
                 (no UTC offset - pass the IANA zone separately via `timezone`)
    timezone:    IANA timezone name, e.g. "Europe/Madrid", "America/New_York"

    Returns the created event dict (includes event["htmlLink"]).
    """
    creds = get_credentials()
    service = build("calendar", "v3", credentials=creds)

    event_body = {
        "summary": title,
        "description": description,
        "start": {"dateTime": start, "timeZone": timezone},
        "end": {"dateTime": end, "timeZone": timezone},
    }
    if attendees:
        event_body["attendees"] = [{"email": a} for a in attendees]

    return service.events().insert(calendarId=calendar_id, body=event_body).execute()


def main():
    parser = argparse.ArgumentParser(description="Create a Google Calendar event.")
    parser.add_argument("--title", required=True)
    parser.add_argument("--start", required=True, help="ISO 8601, e.g. 2026-10-05T15:00:00")
    parser.add_argument("--end", required=True, help="ISO 8601, e.g. 2026-10-05T15:30:00")
    parser.add_argument("--timezone", required=True, help="IANA tz, e.g. Europe/Madrid")
    parser.add_argument("--description", default="")
    args = parser.parse_args()

    event = create_event(
        title=args.title,
        start=args.start,
        end=args.end,
        timezone=args.timezone,
        description=args.description,
    )
    print(f"Event created: {event.get('htmlLink')}")


if __name__ == "__main__":
    main()
