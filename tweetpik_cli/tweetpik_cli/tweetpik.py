from __future__ import annotations

import asyncio
# NOTE: couple sources
# https://github.com/powerfist01/hawk-eyed/blob/f340c6ff814dd3e2a3cac7a30d03b7c07d95d1e4/services/tweet_to_image/tweetpik.py
# https://github.com/bwhli/birdcatcher/blob/a4b33feff4f2d88d5412cd50b11760312bdd4f1d/app/util/Tweet.py
import base64
from io import BytesIO
import json
# pylint: disable=unused-import
import logging
import os
import re
import sys
import unicodedata
from urllib.parse import quote as _uriquote
import weakref

import typing
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Coroutine,
    Dict,
    Iterable,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
)

from PIL import Image
import aiofiles
import aiohttp
import bpdb
from codetiming import Timer
from pydantic import BaseSettings, Field, validator
# from pydantic.main import BaseModel
import requests
import rich
import six
import pathlib


def _to_json(obj: Any) -> str:
    return json.dumps(obj, separators=(",", ":"), ensure_ascii=True)


_from_json = json.loads


# import cerebro_bot
from tweetpik_cli.dbx_logger import get_logger  # noqa: E402

LOGGER = get_logger(__name__, provider="Tweetpik", level=logging.DEBUG)

TWEETPIK_AUTHORIZATION = os.environ.get("TWEETPIK_AUTHORIZATION")
TWEETPIK_BUCKET_ID = os.environ.get("TWEETPIK_BUCKET_ID")

TWEETPIK_DIMENSION_IG_FEED = "1:1"
TWEETPIK_DIMENSION_IG_STORY = "9:16"
TWEETPIK_TIMEZONE = "America/New_York"
TWEETPIK_DISPLAY_LIKES = False
TWEETPIK_DISPLAY_REPLIES = False
TWEETPIK_DISPLAY_RETWEETS = False
TWEETPIK_DISPLAY_VERIFIED = True
TWEETPIK_DISPLAY_SOURCE = True
TWEETPIK_DISPLAY_TIME = True
TWEETPIK_DISPLAY_MEDIA_IMAGES = True
TWEETPIK_DISPLAY_LINK_PREVIEW = True
TWEETPIK_TEXT_WIDTH = (
    "100"  # Any number higher than zero. This value is representing a percentage
)
TWEETPIK_CANVAS_WIDTH = (
    "510"  # Any number higher than zero. This value is used in pixels(px) units
)
# TWEETPIK_BACKGROUND_IMAGE = "510"  # A image that you want to use as background. You need to use this as a valid URL like https://mysite.com/image.png and it should not be protected by CORS

TWEETPIK_BACKGROUND_COLOR = (
    "#FFFFFF"  # Change the background color of the tweet screenshot
)
TWEETPIK_TEXT_PRIMARY_COLOR = "#000000"  # Change the text primary color used for the main text of the tweet and user's name
TWEETPIK_TEXT_SECONDARY_COLOR = "#5B7083"  # Change the text secondary used for the secondary info of the tweet like the username
TWEETPIK_LINK_COLOR = (
    "#1B95E0"  # Change the link colors used for the links, hashtags and mentions
)
TWEETPIK_VERIFIED_ICON = "#1B95E0"  # Change the verified icon color

DEFAULT_TWEETPIK_OPTIONS = {}

if TYPE_CHECKING:
    from aiohttp import ClientResponse

    try:
        from requests import Response

        _ResponseType = Union[ClientResponse, Response]
    except ModuleNotFoundError:
        _ResponseType = ClientResponse

    Snowflake = Union[str, int]
    SnowflakeList = List[Snowflake]

    from types import TracebackType

    T = TypeVar("T")
    BE = TypeVar("BE", bound=BaseException)
    MU = TypeVar("MU", bound="MaybeUnlock")
    Response = Coroutine[Any, Any, T]


class _MissingSentinel:
    def __eq__(self, other):
        return False

    def __bool__(self):
        return False

    def __repr__(self):
        return "..."


MISSING: Any = _MissingSentinel()

def get_tweet_id(tweet_url: str) -> str:
    tweet_id = re.findall(
        r"[http?s//]?twitter\.com\/.*\/status\/(\d+)", tweet_url
    )[0]
    return tweet_id


def build_tweetpik_download_url(tweetId: str) -> str:
    """Building the URL
    The URL is predictable, so you don't have to worry about storing it. You just need to make sure you generated it before using it. The URL will always consist of your bucket ID and the tweet ID. https://ik.imagekit.io/tweetpik/323251495115948625/tweetId

    Returns:
        str: Url of the image we plan to download
    """
    return f"https://ik.imagekit.io/tweetpik/{TWEETPIK_BUCKET_ID}/{tweetId}"


class TweetpikAPIError(Exception):
    """
    Exception for errors thrown by the API. Contains the HTTP status code and the returned error message.
    """

    def __init__(self, status: int, message: typing.Union[str, dict]):
        self.status = status
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        if isinstance(self.message, str):
            try:
                self.message = json.loads(self.message)
                return f'{self.status} {self.message["error_summary"]}'
            except:
                return f"{self.status} {self.message}"
        else:
            return f"{self.status} {self.message}"


class TweetpikException(Exception):
    """Base exception class for tweetpik

    Ideally speaking, this could be caught to handle any exceptions raised from this library.
    """


class ClientException(TweetpikException):
    """Exception that's raised when an operation in the :class:`Client` fails.

    These are usually for exceptions that happened due to user input.
    """


class NoMoreItems(TweetpikException):
    """Exception that is raised when an async iteration operation has no more items."""


class GatewayNotFound(TweetpikException):
    """An exception that is raised when the gateway for Tweetpik could not be found"""

    def __init__(self):
        message = "The gateway to connect to discord was not found."
        super().__init__(message)


def _flatten_error_dict(d: Dict[str, Any], key: str = "") -> Dict[str, str]:
    items: List[Tuple[str, str]] = []
    for k, v in d.items():
        new_key = key + "." + k if key else k

        if isinstance(v, dict):
            try:
                _errors: List[Dict[str, Any]] = v["_errors"]
            except KeyError:
                items.extend(_flatten_error_dict(v, new_key).items())
            else:
                items.append((new_key, " ".join(x.get("message", "") for x in _errors)))
        else:
            items.append((new_key, v))

    return dict(items)


class HTTPException(TweetpikException):
    """Exception that's raised when an HTTP request operation fails.

    Attributes
    ------------
    response: :class:`aiohttp.ClientResponse`
        The response of the failed HTTP request. This is an
        instance of :class:`aiohttp.ClientResponse`. In some cases
        this could also be a :class:`requests.Response`.

    text: :class:`str`
        The text of the error. Could be an empty string.
    status: :class:`int`
        The status code of the HTTP request.
    code: :class:`int`
        The Tweetpik specific error code for the failure.
    """

    def __init__(
        self, response: _ResponseType, message: Optional[Union[str, Dict[str, Any]]]
    ):
        self.response: _ResponseType = response
        self.status: int = response.status  # type: ignore
        self.code: int
        self.text: str
        if isinstance(message, dict):
            self.code = message.get("code", 0)
            base = message.get("message", "")
            errors = message.get("errors")
            if errors:
                errors = _flatten_error_dict(errors)
                helpful = "\n".join("In %s: %s" % t for t in errors.items())
                self.text = base + "\n" + helpful
            else:
                self.text = base
        else:
            self.text = message or ""
            self.code = 0

        fmt = "{0.status} {0.reason} (error code: {1})"
        if len(self.text):
            fmt += ": {2}"

        super().__init__(fmt.format(self.response, self.code, self.text))


class Forbidden(HTTPException):
    """Exception that's raised for when status code 403 occurs.

    Subclass of :exc:`HTTPException`
    """


class NotFound(HTTPException):
    """Exception that's raised for when status code 404 occurs.

    Subclass of :exc:`HTTPException`
    """


class TweetpikServerError(HTTPException):
    """Exception that's raised for when a 500 range status code occurs.

    Subclass of :exc:`HTTPException`.

    .. versionadded:: 1.5
    """


class InvalidData(ClientException):
    """Exception that's raised when the library encounters unknown
    or invalid data from Tweetpik.
    """


class InvalidArgument(ClientException):
    """Exception that's raised when an argument to a function
    is invalid some way (e.g. wrong value or wrong type).

    This could be considered the analogous of ``ValueError`` and
    ``TypeError`` except inherited from :exc:`ClientException` and thus
    :exc:`TweetpikException`.
    """


class ConnectionClosed(ClientException):
    """Exception that's raised when the gateway connection is
    closed for reasons that could not be handled internally.

    Attributes
    -----------
    code: :class:`int`
        The close code of the websocket.
    reason: :class:`str`
        The reason provided for the closure.
    shard_id: Optional[:class:`int`]
        The shard ID that got closed if applicable.
    """

    def __init__(self, socket: ClientResponse, *, code: Optional[int] = None):
        # This exception is just the same exception except
        # reconfigured to subclass ClientException for users
        self.code: int = code or socket.close_code or -1
        # aiohttp doesn't seem to consistently provide close reason
        self.reason: str = ""
        super().__init__(f"HTTP Request closed with {self.code}")


# SOURCE: discord.py
async def json_or_text(response: aiohttp.ClientResponse) -> Union[Dict[str, Any], str]:
    text = await response.text(encoding="utf-8")
    try:
        if response.headers["content-type"] == "application/json":
            return _from_json(text)
    except KeyError:
        # Thanks Cloudflare
        pass

    return text


# SOURCE: discord.py
class TweetpikRoute:
    BASE: ClassVar[str] = "https://tweetpik.com/api"

    def __init__(self, method: str, path: str, **parameters: Any) -> None:
        self.path: str = path
        self.method: str = method
        url = self.BASE + self.path
        if parameters:
            url = url.format_map(
                {
                    k: _uriquote(v) if isinstance(v, str) else v
                    for k, v in parameters.items()
                }
            )
        self.url: str = url
        self.bucket_id: str = TWEETPIK_BUCKET_ID


    @property
    def bucket(self) -> str:
        # the bucket is just method + path w/ major parameters
        return f'{self.bucket_id}'


# SOURCE: discord.py
class MaybeUnlock:
    def __init__(self, lock: asyncio.Lock) -> None:
        self.lock: asyncio.Lock = lock
        self._unlock: bool = True

    def __enter__(self: MU) -> MU:
        return self

    def defer(self) -> None:
        self._unlock = False

    def __exit__(
        self,
        exc_type: Optional[Type[BE]],
        exc: Optional[BE],
        traceback: Optional[TracebackType],
    ) -> None:
        if self._unlock:
            self.lock.release()


# SOURCE: discord.py
class TweetpikHTTPClient:
    """Represents an HTTP client sending HTTP requests to the Tweetpik API."""

    def __init__(
        self,
        connector: Optional[aiohttp.BaseConnector] = None,
        *,
        proxy: Optional[str] = None,
        proxy_auth: Optional[aiohttp.BasicAuth] = None,
        loop: Optional[asyncio.AbstractEventLoop] = None,
        unsync_clock: bool = True,
    ) -> None:
        self.loop: asyncio.AbstractEventLoop = (
            asyncio.get_event_loop() if loop is None else loop
        )
        self.connector = connector
        # self.__session: aiohttp.ClientSession = MISSING  # filled in static_login
        self.__session: aiohttp.ClientSession = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(limit_per_host=50)
        )
        self._locks: weakref.WeakValueDictionary = weakref.WeakValueDictionary()
        self._global_over: asyncio.Event = asyncio.Event()
        self._global_over.set()
        self.token: Optional[str] = None
        self.bot_token: bool = False
        self.proxy: Optional[str] = proxy
        self.proxy_auth: Optional[aiohttp.BasicAuth] = proxy_auth
        self.use_clock: bool = not unsync_clock

        user_agent = "TweetpikHTTPClient (https://github.com/universityofprofessorex/cerebro-bot {0}) Python/{1[0]}.{1[1]} aiohttp/{2}"
        self.user_agent: str = user_agent.format(
            "0.1.0", sys.version_info, aiohttp.__version__
        )

    async def request(
        self,
        route: TweetpikRoute,
        *,
        # files: Optional[Sequence[File]] = None,
        form: Optional[Iterable[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> Any:
        bucket = route.bucket
        method = route.method
        url = route.url

        lock = self._locks.get(bucket)
        if lock is None:
            lock = asyncio.Lock()
            if bucket is not None:
                self._locks[bucket] = lock

        # header creation
        headers: Dict[str, str] = {
            "User-Agent": self.user_agent,
            "Authorization": TWEETPIK_AUTHORIZATION
        }

        # if self.token is not None:
        #     headers["Authorization"] = TWEETPIK_AUTHORIZATION

        # some checking if it's a JSON request
        # if 'json' in kwargs:
        headers["Content-Type"] = "application/json"
        kwargs["data"] = _to_json(kwargs.pop("json"))

        kwargs["headers"] = headers

        # Proxy support
        if self.proxy is not None:
            kwargs["proxy"] = self.proxy
        if self.proxy_auth is not None:
            kwargs["proxy_auth"] = self.proxy_auth

        if not self._global_over.is_set():
            # wait until the global lock is complete
            await self._global_over.wait()

        response: Optional[aiohttp.ClientResponse] = None
        data: Optional[Union[Dict[str, Any], str]] = None
        await lock.acquire()
        with MaybeUnlock(lock) as maybe_lock:
            for tries in range(5):
                # if files:
                #     for f in files:
                #         f.reset(seek=tries)

                # if form:
                #     form_data = aiohttp.FormData()
                #     for params in form:
                #         form_data.add_field(**params)
                #     kwargs['data'] = form_data

                try:
                    async with self.__session.request(
                        method, url, **kwargs
                    ) as response:
                        LOGGER.debug(
                            f"{method} {url} with {kwargs.get('data')} has returned {response.status}"
                        )

                        # even errors have text involved in them so this is safe to call
                        data = await json_or_text(response)

                        LOGGER.debug(
                            "HERE IS THE DATA WE GET BACK FROM THE API CALL BELOVED"
                        )
                        LOGGER.debug(data)

                        # # check if we have rate limit header information
                        # remaining = response.headers.get('X-Ratelimit-Remaining')
                        # if remaining == '0' and response.status != 429:
                        #     # we've depleted our current bucket
                        #     delta = utils._parse_ratelimit_header(response, use_clock=self.use_clock)
                        #     LOGGER.debug('A rate limit bucket has been exhausted (bucket: %s, retry: %s).', bucket, delta)
                        #     maybe_lock.defer()
                        #     self.loop.call_later(delta, lock.release)

                        # the request was successful so just return the text/json
                        if 300 > response.status >= 200:
                            LOGGER.debug(f"{method} {url} has received {data}")
                            return data

                        # we are being rate limited
                        if response.status == 429:
                            if not response.headers.get("Via") or isinstance(data, str):
                                # Banned by Cloudflare more than likely.
                                raise HTTPException(response, data)

                            fmt = 'We are being rate limited. Retrying in %.2f seconds. Handled under the bucket "%s"'

                            # sleep a bit
                            retry_after: float = data["retry_after"]
                            LOGGER.warning(fmt, retry_after, bucket)

                            # # check if it's a global rate limit
                            # is_global = data.get('global', False)
                            # if is_global:
                            #     LOGGER.warning('Global rate limit has been hit. Retrying in %.2f seconds.', retry_after)
                            #     self._global_over.clear()

                            # await asyncio.sleep(retry_after)
                            # LOGGER.debug('Done sleeping for the rate limit. Retrying...')

                            # # release the global lock now that the
                            # # global rate limit has passed
                            # if is_global:
                            #     self._global_over.set()
                            #     LOGGER.debug('Global rate limit is now over.')

                            continue

                        # we've received a 500, 502, or 504, unconditional retry
                        if response.status in {500, 502, 504}:
                            await asyncio.sleep(1 + tries * 2)
                            continue

                        # the usual error cases
                        if response.status == 403:
                            raise Forbidden(response, data)
                        elif response.status == 404:
                            raise NotFound(response, data)
                        elif response.status >= 500:
                            raise TweetpikServerError(response, data)
                        else:
                            raise HTTPException(response, data)

                # This is handling exceptions from the request
                except OSError as e:
                    # Connection reset by peer
                    if tries < 4 and e.errno in (54, 10054):
                        await asyncio.sleep(1 + tries * 2)
                        continue
                    raise

            if response is not None:
                # We've run out of retries, raise.
                if response.status >= 500:
                    raise TweetpikServerError(response, data)

                raise HTTPException(response, data)

            raise RuntimeError("Unreachable code in HTTP handling")

    async def get_from_cdn(self, url: str) -> bytes:
        async with self.__session.get(url) as resp:
            if resp.status == 200:
                return await resp.read()
            elif resp.status == 404:
                raise NotFound(resp, "asset not found")
            elif resp.status == 403:
                raise Forbidden(resp, "cannot retrieve asset")
            else:
                raise HTTPException(resp, "failed to get asset")

    # state management

    async def close(self) -> None:
        if self.__session:
            await self.__session.close()

    def images(
        self,
        tweet_url: Optional[str],
        *,
        dimension_ig_feed: Optional[str] = TWEETPIK_DIMENSION_IG_FEED,
        dimension_ig_story: Optional[str] = TWEETPIK_DIMENSION_IG_STORY,
        timezone: Optional[str] = TWEETPIK_TIMEZONE,
        display_likes: Optional[str] = TWEETPIK_DISPLAY_LIKES,
        display_replies: Optional[str] = TWEETPIK_DISPLAY_REPLIES,
        display_retweets: Optional[str] = TWEETPIK_DISPLAY_RETWEETS,
        display_verified: Optional[str] = TWEETPIK_DISPLAY_VERIFIED,
        display_source: Optional[str] = TWEETPIK_DISPLAY_SOURCE,
        display_time: Optional[str] = TWEETPIK_DISPLAY_TIME,
        display_media_images: Optional[str] = TWEETPIK_DISPLAY_MEDIA_IMAGES,
        display_link_preview: Optional[str] = TWEETPIK_DISPLAY_LINK_PREVIEW,
        text_width: Optional[str] = TWEETPIK_TEXT_WIDTH,
        canvas_width: Optional[str] = TWEETPIK_CANVAS_WIDTH,
        background_color: Optional[str] = TWEETPIK_BACKGROUND_COLOR,
        text_primary_color: Optional[str] = TWEETPIK_TEXT_PRIMARY_COLOR,
        text_secondary_color: Optional[str] = TWEETPIK_TEXT_SECONDARY_COLOR,
        link_color: Optional[str] = TWEETPIK_LINK_COLOR,
        verified_icon: Optional[str] = TWEETPIK_VERIFIED_ICON,
    ) -> Any:
        r = TweetpikRoute("POST", "/images", tweet_url=tweet_url)
        payload = {}

        # if tweet_url:
        #     payload["tweet_url"] = tweet_url
        if tweet_url:
            payload["tweetId"] = get_tweet_id(tweet_url)

        if dimension_ig_feed:
            payload["dimension_ig_feed"] = dimension_ig_feed
        if dimension_ig_story:
            payload["dimension_ig_story"] = dimension_ig_story
        if timezone:
            payload["timezone"] = timezone
        if display_likes:
            payload["display_likes"] = display_likes
        if display_replies:
            payload["display_replies"] = display_replies
        if display_retweets:
            payload["display_retweets"] = display_retweets
        if display_verified:
            payload["display_verified"] = display_verified
        if display_source:
            payload["display_source"] = display_source
        if display_time:
            payload["display_time"] = display_time
        if display_media_images:
            payload["display_media_images"] = display_media_images
        if display_link_preview:
            payload["display_link_preview"] = display_link_preview
        if text_width:
            payload["text_width"] = text_width
        if canvas_width:
            payload["canvas_width"] = canvas_width
        if background_color:
            payload["background_color"] = background_color
        if text_primary_color:
            payload["text_primary_color"] = text_primary_color
        if text_secondary_color:
            payload["text_secondary_color"] = text_secondary_color
        if link_color:
            payload["link_color"] = link_color
        if verified_icon:
            payload["verified_icon"] = verified_icon

        LOGGER.debug("payload debuggggggggggggggggggggggggggg")
        LOGGER.debug(payload)

        return self.request(r, json=payload)

    async def aimages(
        self,
        tweet_url: Optional[str],
        *,
        dimension_ig_feed: Optional[str] = TWEETPIK_DIMENSION_IG_FEED,
        dimension_ig_story: Optional[str] = TWEETPIK_DIMENSION_IG_STORY,
        timezone: Optional[str] = TWEETPIK_TIMEZONE,
        display_likes: Optional[str] = TWEETPIK_DISPLAY_LIKES,
        display_replies: Optional[str] = TWEETPIK_DISPLAY_REPLIES,
        display_retweets: Optional[str] = TWEETPIK_DISPLAY_RETWEETS,
        display_verified: Optional[str] = TWEETPIK_DISPLAY_VERIFIED,
        display_source: Optional[str] = TWEETPIK_DISPLAY_SOURCE,
        display_time: Optional[str] = TWEETPIK_DISPLAY_TIME,
        display_media_images: Optional[str] = TWEETPIK_DISPLAY_MEDIA_IMAGES,
        display_link_preview: Optional[str] = TWEETPIK_DISPLAY_LINK_PREVIEW,
        text_width: Optional[str] = TWEETPIK_TEXT_WIDTH,
        canvas_width: Optional[str] = TWEETPIK_CANVAS_WIDTH,
        background_color: Optional[str] = TWEETPIK_BACKGROUND_COLOR,
        text_primary_color: Optional[str] = TWEETPIK_TEXT_PRIMARY_COLOR,
        text_secondary_color: Optional[str] = TWEETPIK_TEXT_SECONDARY_COLOR,
        link_color: Optional[str] = TWEETPIK_LINK_COLOR,
        verified_icon: Optional[str] = TWEETPIK_VERIFIED_ICON,
    ) -> Any:
        r = TweetpikRoute("POST", "/images", tweet_url=tweet_url)
        payload = {}

        if tweet_url:
            payload["tweetId"] = get_tweet_id(tweet_url)

        if dimension_ig_feed:
            payload["dimension_ig_feed"] = dimension_ig_feed
        if dimension_ig_story:
            payload["dimension_ig_story"] = dimension_ig_story
        if timezone:
            payload["timezone"] = timezone
        if display_likes:
            payload["display_likes"] = display_likes
        if display_replies:
            payload["display_replies"] = display_replies
        if display_retweets:
            payload["display_retweets"] = display_retweets
        if display_verified:
            payload["display_verified"] = display_verified
        if display_source:
            payload["display_source"] = display_source
        if display_time:
            payload["display_time"] = display_time
        if display_media_images:
            payload["display_media_images"] = display_media_images
        if display_link_preview:
            payload["display_link_preview"] = display_link_preview
        if text_width:
            payload["text_width"] = text_width
        if canvas_width:
            payload["canvas_width"] = canvas_width
        if background_color:
            payload["background_color"] = background_color
        if text_primary_color:
            payload["text_primary_color"] = text_primary_color
        if text_secondary_color:
            payload["text_secondary_color"] = text_secondary_color
        if link_color:
            payload["link_color"] = link_color
        if verified_icon:
            payload["verified_icon"] = verified_icon

        LOGGER.debug("payload debuggggggggggggggggggggggggggg")
        LOGGER.debug(payload)
        data = await self.request(r, json=payload)
        await self.close()

        return data

# TODO: implement multi download https://stackoverflow.com/questions/64282309/aiohttp-download-large-list-of-pdf-files
async def async_download_file(data: dict, dl_dir="./"):
    async with aiohttp.ClientSession() as session:
        url: str = data["url"]
        username: str = data["tweet"]["username"]
        p = pathlib.Path(url)
        p_dl_dir = pathlib.Path(dl_dir)
        full_path_dl_dir = f"{p_dl_dir.absolute()}"
        LOGGER.debug(f"Downloading {url} to {full_path_dl_dir}/{p.name}")
        async with session.get(url) as resp:
            content = await resp.read()

            # Check everything went well
            if resp.status != 200:
                LOGGER.error(f"Download failed: {resp.status}")
                return

            if resp.status == 200:
                async with aiofiles.open(f"{full_path_dl_dir}/{p.name}", mode="+wb") as f:
                    await f.write(content)
                    # No need to use close(f) when using with statement
                # f = await aiofiles.open(f"{full_path_dl_dir}/{p.name}", mode='wb')
                # await f.write(await resp.read())
                # await f.close()

# SOURCE: https://github.com/powerfist01/hawk-eyed/blob/f340c6ff814dd3e2a3cac7a30d03b7c07d95d1e4/services/tweet_to_image/tweetpik.py
class TweetPik:
    """
    TweetPik API client using asynchronous HTTP requests.

    Args:
        tweet_url:
            url of tweet we want to download [str]
        retry_statuses:
            list of statuses that will automatically be retried (default is [429])
    """

    tweetpik_uri = "https://tweetpik.com/api/images"
    headers = {
        "Content-Type": "application/json",
        "authorization": os.environ["TWEETPIK_AUTHORIZATION"],
    }

    def __init__(self, tweet_url: str, retry_statuses: list[int] = [429]):
        """Default constructor"""
        self.tweet_url = tweet_url
        self.tweet_id = self.get_tweet_id()
        self.retry_statuses = retry_statuses
        self.client_session = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(limit_per_host=50)
        )
        self.upload_session: list[dict] = []

    def get_tweet_id(self) -> str:
        tweet_id = re.findall(
            r"[http?s//]?twitter\.com\/.*\/status\/(\d+)", self.tweet_url
        )[0]
        return tweet_id

    def fetch_tweet_image_url(self):
        """To download get the url of the tweet image from tweetpik"""
        try:
            data = {"tweetId": self.tweet_id}

            response = requests.post(
                self.tweetpik_uri, headers=self.headers, data=json.dumps(data)
            )

            if response.status_code == 201:
                data = response.json()
                return data["url"]
            else:
                print("Error occured in fetching the image!")
        except Exception as e:
            print(e)

    def download_image_using_tweet_id(self):
        """To download the image using url"""

        image_url = self.fetch_tweet_image_url()

        res = requests.get(image_url, stream=True)
        if res.status_code == 200:
            path = "downloads/" + image_url.split("/")[-1]
            with open(path, "wb") as f:
                for chunk in res:
                    f.write(chunk)
            path = self.crop_image(path)
            return path
        else:
            print("Error Occured in downloading image!")

    def crop_image(self, path):
        """To crop the image using PILLOW"""

        with Image.open(path) as im:

            width, height = im.size  # Get dimensions
            left = width / 1000
            top = height / 10
            right = width - width / 1000
            bottom = height - height / 1000

            # Here the image "im" is cropped and assigned to new variable im_crop
            im_crop = im.crop((left, top, right, bottom))

            im_crop.save(path, "png")

        if str(path).endswith(".png"):
            path = self.convert_to_jpeg(path)

        return path

    def convert_to_jpeg(self, path):
        """To convert to jpg"""

        im = Image.open(path)
        rgb_im = im.convert("RGB")
        path = path.replace(".png", ".jpg")
        rgb_im.save(path)
        return path


# SOURCE: https://github.com/bwhli/birdcatcher/blob/a4b33feff4f2d88d5412cd50b11760312bdd4f1d/app/util/Tweet.py
class Tweet:
    def __init__(self, tweet_url: str):
        self.tweet_url = tweet_url

    def get_tweet_id(self) -> str:
        tweet_id = re.findall(
            r"[http?s//]?twitter\.com\/.*\/status\/(\d+)", self.tweet_url
        )[0]
        return tweet_id

    def get_tweet_user(self) -> str:
        tweet_user = re.findall(
            r"[http?s//]?twitter\.com\/(.*)\/status\/\d+", self.tweet_url
        )[0]
        return tweet_user

    def get_tweet_body(self) -> str:
        if self.is_valid_tweet() == True:
            tweet_id = self.get_tweet_id()
            api_endpoint = f"https://api.twitter.com/2/tweets?ids={tweet_id}&tweet.fields=author_id,conversation_id,created_at,source"
            request_headers = {"Authorization": "Bearer"}
            response = requests.get(
                api_endpoint, headers=request_headers, timeout=5
            ).json()["data"][0]
            return json.dumps(response, ensure_ascii=False, sort_keys=True)
        else:
            return "Tweet ID is invalid."

    def generate_tweet_image_url(self):
        tweet_id = self.get_tweet_id()
        headers = {
            "Content-Type": "application/json",
            "Authorization": "",
        }
        data = {"tweetId": str(tweet_id)}
        response = requests.post(
            "https://tweetpik.com/api/images", headers=headers, data=json.dumps(data)
        ).json()
        image_url = response["url"]
        return image_url

    def generate_tweet_image_b64_string(self):
        image_url = self.generate_tweet_image_url()
        response = requests.get(image_url, stream=True)
        response.raw.decode_content = True
        image = Image.open(response.raw)
        buffered = BytesIO()
        image.save(buffered, format="PNG", optimize=True)
        tweet_image_b64_string = (
            f"data:image/png;base64,{base64.b64encode(buffered.getvalue()).decode()}"
        )
        return tweet_image_b64_string

    def is_valid_tweet(self) -> bool:
        tweet_id = self.get_tweet_id()
        api_endpoint = f"https://api.twitter.com/2/tweets?ids={tweet_id}"
        request_headers = {"Authorization": "Bearer"}
        response = requests.get(api_endpoint, headers=request_headers, timeout=5).json()
        if "errors" in response:
            return False
        else:
            return True
