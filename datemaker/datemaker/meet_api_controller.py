import os

from google.apps.meet_v2 import Space
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.apps import meet_v2

from datemaker import setup_logger

# If modifying these scopes, delete the file token.json.
SCOPES = [
    'https://www.googleapis.com/auth/meetings.space.created'
]

LOGGER = setup_logger(__name__)


class GoogleMeetApiController:
    def __init__(self, creds_file_path: str, token_file_path: str = None):
        self.token_file_path = token_file_path
        self.creds_file_path = creds_file_path
        self.client = meet_v2.SpacesServiceAsyncClient(
            credentials=self._read_creds()
        )

    async def create_space(self) -> Space:
        space = await self.client.create_space(
            request=meet_v2.CreateSpaceRequest()
        )
        LOGGER.debug(f'New space {space.name} created.')
        return space

    async def end_active_call(self, space: Space):
        LOGGER.debug(f'Ending active call in space {space.name}')
        await self.client.end_active_conference(
            request=meet_v2.EndActiveConferenceRequest(
                name=space.name,
            )
        )

    def _read_creds(self):
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        creds = None

        if os.path.exists(self.token_file_path):
            creds = Credentials.from_authorized_user_file(
                self.token_file_path,
                SCOPES
            )

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.creds_file_path,
                    SCOPES
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(self.token_file_path, 'w') as token:
                token.write(creds.to_json())

        return creds
