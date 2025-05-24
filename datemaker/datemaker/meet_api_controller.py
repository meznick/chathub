import asyncio
import os
from asyncio import AbstractEventLoop

from google.apps import meet_v2
from google.apps.meet_v2 import UpdateSpaceRequest, SpaceConfig, Space
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from datemaker import setup_logger

# If modifying these scopes, delete the file token.json.
SCOPES = [
    'https://www.googleapis.com/auth/meetings.space.created'
]

LOGGER = setup_logger(__name__)


class GoogleMeetApiController:
    def __init__(
            self,
            creds_file_path: str,
            token_file_path: str = None,
    ):
        self.token_file_path = token_file_path
        self.creds_file_path = creds_file_path
        self.client = None
        self.event_loop: AbstractEventLoop = None

    def connect(self, custom_event_loop: AbstractEventLoop = None):
        self.client = meet_v2.SpacesServiceAsyncClient(
            credentials=self._read_creds()
        )
        self.event_loop = custom_event_loop or asyncio.get_running_loop()

    async def create_space(self) -> Space:
        coro = self.client.create_space(
            request=meet_v2.CreateSpaceRequest()
        )
        space = await self.event_loop.create_task(coro)
        LOGGER.debug(f'New space {space.name} created.')
        return space

    async def end_active_call(self, space: Space):
        LOGGER.debug(f'Ending active call in space {space.name}')
        coro = self.client.end_active_conference(
            request=meet_v2.EndActiveConferenceRequest(
                name=space.name,
            )
        )
        await self.event_loop.create_task(coro)

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

    async def make_space_public(
            self,
            space_name: str,
            entry_point_access: str = 'ALL',
            access_type: str = 'OPEN'):
        # Создаём объект SpaceConfig
        space_config = SpaceConfig(
            entry_point_access=entry_point_access,
            access_type=access_type
        )

        # Создаём объект Space с обновлённой конфигурацией
        space = Space(
            name=space_name,
            config=space_config
        )

        # Создаём запрос на обновление
        request = UpdateSpaceRequest(
            space=space,
            # Указываем, что обновляем только поле config
            update_mask={"paths": ["config.entry_point_access", "config.access_type"]}
        )

        # Выполняем запрос
        response = await self.client.update_space(request=request)

        LOGGER.debug(f"Space updated: {response.name}")
        return response

    async def create_public_space(self) -> Space:
        space = await self.create_space()
        space = await self.make_space_public(space_name=space.name)
        return space

    async def delete_meeting_with_timer(self, space: Space, timer_minutes: int = 5):
        await asyncio.sleep(timer_minutes * 60)
        await self.end_active_call(space)
        LOGGER.debug(f"Space deleted: {space.name}")
