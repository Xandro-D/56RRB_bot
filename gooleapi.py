import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Your spreadsheet ID - get this from your Google Sheet URL
# URL format: https://docs.google.com/spreadsheets/d/YOUR_SPREADSHEET_ID/edit
SPREADSHEET_ID = "1sglr0ZzpFvZoqgDyuvQ55EKnFrzvPyNAZzpAVPYzapM"  # Replace with your sheet ID

# The range where you want to write data
RANGE_NAME = "Sheet1!A1"  # Change to your sheet name and range


def get_sheets_service():
    """Authenticates and returns the Google Sheets service."""
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return build("sheets", "v4", credentials=creds)


def sheets(data, spreadsheet_id=None, range_name=None, append=False):
    """
  Writes data to a Google Spreadsheet.

  Args:
      data: List of lists containing the data to write
            Example: [['Name', 'Age'], ['Alice', 30], ['Bob', 25]]
      spreadsheet_id: (Optional) Override the default spreadsheet ID
      range_name: (Optional) Override the default range (e.g., 'Sheet1!A1')
      append: (Optional) If True, appends data instead of overwriting

  Returns:
      Number of cells updated/appended
  """
    try:
        service = get_sheets_service()

        # Use provided values or defaults
        sheet_id = spreadsheet_id or SPREADSHEET_ID
        range_to_use = range_name or RANGE_NAME

        body = {'values': data}

        if append:
            # Append data to the end
            result = service.spreadsheets().values().append(
                spreadsheetId=sheet_id,
                range=range_to_use,
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            cells_updated = result.get('updates').get('updatedCells')
            print(f"✅ {cells_updated} cells appended successfully!")
        else:
            # Overwrite data at the specified range
            result = service.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range=range_to_use,
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            cells_updated = result.get('updatedCells')
            print(f"✅ {cells_updated} cells updated successfully!")

        return cells_updated

    except HttpError as err:
        print(f"❌ Error: {err}")
        return None

    # Example usage

# testing
if __name__ == "__main__":
  # Example 1: Simple data
  my_data = [
    ['Name', 'Age', 'City'],
    ['Alice', 30, 'New York'],
    ['Bob', 25, 'Los Angeles'],
    ['Charlie', 35, 'Chicago']
  ]
  sheets(my_data)