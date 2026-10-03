"""
One-time setup script.

Run this ONCE to authorize access to your Google Calendar. It needs
`credentials.json` (OAuth Client ID, type "Desktop app", downloaded from
Google Cloud Console) in the same folder.

Running it opens your browser once to approve access, then saves
`token.json` next to this script. After that, create_calendar_event.py
works without ever opening a browser again (it auto-refreshes the token).

Usage:
    python calendar_auth_setup.py
"""

from google_auth_oauthlib.flow import InstalledAppFlow

# Minimal scope: only lets the app create/edit/delete events it created.
# It cannot read the rest of your calendar or your other Google data.
SCOPES = ["https://www.googleapis.com/auth/calendar.events"]


def main():
    flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
    creds = flow.run_local_server(port=0)

    with open("token.json", "w", encoding="utf-8") as token_file:
        token_file.write(creds.to_json())

    print("Authorization successful. token.json saved in the current folder.")
    print("You can now use create_calendar_event.py without a browser.")


if __name__ == "__main__":
    main()
