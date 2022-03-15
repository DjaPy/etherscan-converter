import asyncio
from functools import wraps
from os.path import join
from typing import Any, Callable, Dict, Generic, Optional, Sequence, Type, TypeVar, Union

from aiohttp import ClientError, ClientResponse, ClientSession, ClientTimeout, Fingerprint, MultipartWriter
from aiohttp.client_exceptions import SSLContext
from pydantic import AnyHttpUrl, BaseModel, BaseSettings, Field
from starlette import status
from yarl import URL


class ConfigClient(BaseSettings):
    url: Optional[AnyHttpUrl] = Field(description='Хост сервиса для клиента')
    timeout: int = Field(10, description='Время ожидания ответа от сервера')


ConfigClass = TypeVar('ConfigClass', bound=ConfigClient)
ResponseModel = TypeVar('ResponseModel', bound=BaseModel)
ErrorSchema = TypeVar('ErrorSchema')
ErrorException = TypeVar('ErrorException', bound=Exception)


class Client(Generic[ConfigClass, ErrorException]):
    cfg: ConfigClient
    session: Optional[ClientSession]
    _exception: Type[ErrorException]

    def __init__(self, config: ConfigClient) -> None:
        self.session = None
        self.cfg = config
        if self.cfg.url:
            self.url = URL(self.cfg.url)

    async def start(self) -> None:
        self.session = ClientSession(timeout=ClientTimeout(self.cfg.timeout))

    async def stop(self) -> None:
        if self.session:
            await self.session.close()

    async def _error_handler(self, error_schema: Type[ErrorSchema], response: ClientResponse) -> Optional[ErrorSchema]:
        response_r = await response.read()
        error = error_schema.parse_raw(response_r)  # type: ignore
        error.status_code = response.status
        return error

    async def _success_handler(self, response_schema: Type[ResponseModel], response: ClientResponse) -> ResponseModel:
        return response_schema.parse_raw(await response.read())

    async def _empty_handler(self, error_schema: Type[ErrorSchema], response: ClientResponse) -> Optional[ErrorSchema]:
        return None

    async def get_raw_response(self, url: URL, method: str = 'GET', **kwargs: Any) -> ClientResponse:
        if not self.session:
            raise RuntimeError('Session is not initialize. Call .start()')

        try:
            response: ClientResponse = await self.session.request(
                method=method,
                url=url,
                timeout=ClientTimeout(total=(self.cfg.timeout or 10.0)),
                **kwargs,
            )
        except (asyncio.TimeoutError, ClientError):
            raise self._exception(f'Service unavailable, url="{url}"')

        return response

    async def _send_request(
        self,
            path: str,
            response_schema: Type[ResponseModel],
            error_schema: Type[ErrorSchema],
            method: str = 'GET',
            ssl: Optional[Union[SSLContext, bool, Fingerprint]] = False,
            headers: Optional[Dict[str, str]] = None,
            body: Optional[Union[Dict[str, Any], MultipartWriter, str, bytes]] = None,
            **kwargs: Optional[Any]
    ) -> Union[Optional[ResponseModel], Optional[ErrorSchema]]:

        url = str(self.url.with_path(join(self.url.path, path)))
        if not self.session:
            raise RuntimeError('Session is not initialize. Call .start()')
        try:
            response: ClientResponse = await self.session.request(
                method=method,
                url=url,
                headers=headers,
                data=body,
                timeout=ClientTimeout(total=(self.cfg.timeout or 10.0)),
                ssl=ssl,
                **kwargs,
            )
        except asyncio.TimeoutError:
            raise self._exception({'errors': 'Service unavailable'})
        if response.status in (status.HTTP_200_OK, status.HTTP_201_CREATED):
            return await self._success_handler(response_schema, response)

        if response.status in (status.HTTP_404_NOT_FOUND, status.HTTP_204_NO_CONTENT):
            return await self._empty_handler(error_schema, response)

        if response.status in (status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN):
            return await self._error_handler(error_schema, response)

        raise self._exception(f'Error in request "{response.status}" method="{method}", url="{url}"')


def repeat_call_on_exception(
        exception: Union[Type[Exception], Sequence[Type[Exception]]],
        count: int,
        timeout: float
) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwrags: Any) -> Callable:
            _exception: Optional[Exception] = None
            for _ in range(count):
                try:
                    return await func(*args, **kwrags)
                except exception as error:  # type:ignore
                    _exception = error
                    await asyncio.sleep(timeout)
            raise _exception  # type:ignore
        setattr(wrapper, 'func', func)
        return wrapper
    return decorator
