# pylint: disable=no-name-in-module
import logging
import os
from pathlib import Path
import subprocess
import sys
import time
import asyncio
import tempfile
import asyncio
import logging
import os
import pathlib
import tempfile
import aiofiles
import traceback

from codetiming import Timer

from IPython.core import ultratb
from IPython.core.debugger import Tracer  # noqa
from PIL import Image
from fastapi import Depends, FastAPI, File, Header, HTTPException, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import UJSONResponse
import numpy as np
from prometheus_fastapi_instrumentator import Instrumentator, metrics
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import (
    JSONResponse,
    PlainTextResponse,
    RedirectResponse,
    Response,
)
from starlette.staticfiles import StaticFiles
import tensorflow as tf
from tensorflow.keras.applications.imagenet_utils import (  # pylint: disable=no-name-in-module
    decode_predictions,
)
import uvicorn

from aiopillow import settings
from aiopillow.components import predict, read_imagefile
from aiopillow.components.prediction import symptom_check
from aiopillow.dbx_logger import (  # noqa: E402
    generate_tree,
    get_lm_from_tree,
    get_logger,
    intercept_all_loggers,
)
from aiopillow.models.loggers import LoggerModel, LoggerPatch
from aiopillow.schema import Symptom
from aiopillow.utils import writer
from aiopillow import aiodbx

# aiopillow.utils.config

# DROPBOX_AIODROPBOX_APP_KEY = os.environ.get("DROPBOX_AIODROPBOX_APP_KEY")
# DROPBOX_AIODROPBOX_APP_SECRET = os.environ.get("DROPBOX_AIODROPBOX_APP_SECRET")

# DROPBOX_AIODROPBOX_TOKEN = os.environ.get("DROPBOX_AIODROPBOX_TOKEN")
# DEFAULT_DROPBOX_FOLDER = "/cerebro_downloads"

sys.excepthook = ultratb.FormattedTB(
    mode="Verbose", color_scheme="Linux", call_pdb=True, ostream=sys.__stdout__
)

# tenserflow logging
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "0"


LOG_LEVELS = {
    "critical": logging.CRITICAL,
    "error": logging.ERROR,
    "warning": logging.WARNING,
    "info": logging.INFO,
    "debug": logging.DEBUG,
}


app_desc = """<h2>Try this app by uploading any image with `predict/image`</h2>
<h2>Try Covid symptom checker api - it is just a learning app demo</h2>
<br>by Aniket Maurya"""


# SOURCE: https://blog.hipolabs.com/remote-debugging-with-vscode-docker-and-pico-fde11f0e5f1c
def start_debugger():
    parent_pid = os.getppid()
    # cmd = "ps aux | grep %s | awk '{print $2}'" % "ULTRON_ENABLE_WEB"
    cmd = "ps aux | grep 'python aiopillow/web.py' | awk '{print $2}' | head -1"
    ps = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=4096,
        shell=True,
        universal_newlines=True,
    )

    output, _ = ps.communicate()
    pids = output.split("\n")
    # using list comprehension to perform removal of empty strings
    pids = [i for i in pids if i]
    return parent_pid, pids


# LOGGER = get_logger(__name__, provider="Web")
LOGGER = get_logger(__name__, provider="Web", level=logging.DEBUG)
intercept_all_loggers()

FASTAPI_LOGGER = logging.getLogger("fastapi")
FASTAPI_LOGGER.setLevel(logging.DEBUG)


# async def _co_dropbox_upload(dbx: aiodbx.AsyncDropboxAPI, path_to_file: pathlib.PosixPath):

async def run_upload_to_dropbox(dbx: aiodbx.AsyncDropboxAPI, path_to_file: pathlib.PosixPath):
    # upload the new file to an upload session
    # this returns a "commit" dict, which will be passed to upload_finish later
    # the commit is saved in the AsyncDropboxAPI object already, so unless you need
    # information from it you can discard the return value
    await dbx.upload_start(path_to_file, f"/{pathlib.Path(path_to_file).name}")

# @app.exception_handler(RequestValidationError)
# SOURCE: https://fastapi.tiangolo.com/tutorial/handling-errors/#use-the-requestvalidationerror-body
def validation_exception_handler(request: Request, exc: RequestValidationError):
    # print(jsonable_encoder({"detail": exc.errors(), "body": exc.body}))
    print(f"OMG! The client sent invalid data!: {exc}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )


# SOURCE: https://stackoverflow.com/questions/60778279/fastapi-middleware-peeking-into-responses
class LogRequestMiddleware(BaseHTTPMiddleware):
    """Alternate implementation for:

    @app.middleware("http")
    async def db_session_middleware(request: Request, call_next):
        # NOTE: request.state is a property of each Request object. It is there to store arbitrary objects attached to the request itself, like the database session in this case. You can read more about it in Starlette's docs about Request state.
        # For us in this case, it helps us ensure a single database session is used through all the request, and then closed afterwards (in the middleware).
        response = Response("Internal server error", status_code=500)
        try:
            request.state.db = Session()
            response = await call_next(request)
        finally:
            request.state.db.close()
        return response

    Arguments:
        BaseHTTPMiddleware {[type]} -- [description]
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        LOGGER.info(f"{request.method} {request.url}")
        response = await call_next(request)
        LOGGER.info(f"Status code: {response.status_code}")
        body = b""
        async for chunk in response.body_iterator:
            body += chunk
        # do something with body ...
        LOGGER.info("[body]: ")
        LOGGER.info(body)
        return Response(
            content=body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type,
        )


def get_application() -> FastAPI:
    # SOURCE: https://github.com/nwcell/guid_tracker/blob/aef948336ba268aa06df7cc9e7e6768b08d0f363/src/guid/main.py
    app = FastAPI(title="aiopillow Web Server", description=app_desc)

    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    # app.add_exception_handler(Exception, misc_exception_handler)

    LOGGER.info(f"Create fastapi web application ...")

    LOGGER.info(f" settings.DEBUG={settings.DEBUG}")

    app.debug = settings.DEBUG
    app.mount(
        "/static",
        StaticFiles(directory=str(Path(__file__).parent / "static")),
        name="static",
    )

    # CORS
    origins = []

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_methods=[settings.BACKEND_CORS_ORIGINS],
        allow_headers=[settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
    )

    # app.add_middleware(starlette_prometheus.PrometheusMiddleware)

    # instrumentator = Instrumentator(
    #     should_group_status_codes=False,
    #     should_ignore_untemplated=True,
    #     should_respect_env_var=True,
    #     should_instrument_requests_inprogress=True,
    #     excluded_handlers=[".*admin.*", "/metrics"],
    #     env_var_name="ENABLE_METRICS",
    #     inprogress_name="inprogress",
    #     inprogress_labels=True,
    # )

    # app.add_route(f"{settings.API_V1_STR}/metrics", starlette_prometheus.metrics)

    # app.include_router(
    #     log_endpoint.router, tags=["log"], prefix=f"{settings.API_V1_STR}/logs"
    # )
    # app.include_router(token.router, tags=["token"], prefix=f"{settings.API_V1_STR}")
    # app.include_router(home.router, tags=["home"], prefix=f"{settings.API_V1_STR}")
    # app.include_router(alive.router, tags=["alive"], prefix=f"{settings.API_V1_STR}")
    # app.include_router(
    #     version.router, tags=["version"], prefix=f"{settings.API_V1_STR}"
    # )
    # app.include_router(login.router, tags=["login"], prefix=f"{settings.API_V1_STR}")
    # app.include_router(
    #     users.router, tags=["users"], prefix=f"{settings.API_V1_STR}/users"
    # )
    # app.include_router(
    #     items.router,
    #     prefix=f"{settings.API_V1_STR}/items",
    #     tags=["items"],
    #     # dependencies=[Depends(get_token_header)],
    #     # responses={404: {"description": "Not found"}},
    # )

    # app.add_middleware(DbSessionMiddleware)

    # only add this logging middleware if we have this in super debug mode ( since it is noisey )
    if os.getenv("ULTRON_ENVIRONMENT", "production") == "development":
        app.add_middleware(LogRequestMiddleware)

    return app


# # SOURCE: https://fastapi.tiangolo.com/tutorial/sql-databases/#alternative-db-session-with-middleware
# # to we make sure the database session is always closed after the request. Even if there was an exception while processing the request.
# # SOURCE: https://www.starlette.io/middleware/
# class DbSessionMiddleware(BaseHTTPMiddleware):
#     """Alternate implementation for:

#     @app.middleware("http")
#     async def db_session_middleware(request: Request, call_next):
#         # NOTE: request.state is a property of each Request object. It is there to store arbitrary objects attached to the request itself, like the database session in this case. You can read more about it in Starlette's docs about Request state.
#         # For us in this case, it helps us ensure a single database session is used through all the request, and then closed afterwards (in the middleware).
#         response = Response("Internal server error", status_code=500)
#         try:
#             request.state.db = Session()
#             response = await call_next(request)
#         finally:
#             request.state.db.close()
#         return response

#     Arguments:
#         BaseHTTPMiddleware {[type]} -- [description]
#     """

#     async def dispatch(self, request: Request, call_next: Callable) -> Response:
#         response = Response("Internal server error", status_code=500)
#         try:
#             LOGGER.debug(
#                 "[DbSessionMiddleware] dispatch - Creating new Sqlalchemy Session()"
#             )
#             LOGGER.debug(
#                 "[DbSessionMiddleware] dispatch - current thread {}".format(
#                     threading.current_thread().name
#                 )
#             )
#             request.state.db = SessionLocal()
#             LOGGER.debug("[DbSessionMiddleware] dispatch - await call_next(request)")
#             response = await call_next(request)
#         finally:
#             LOGGER.debug(
#                 "[DbSessionMiddleware] dispatch - closing ... request.state.db.close()"
#             )
#             LOGGER.debug(
#                 "[DbSessionMiddleware] dispatch - current thread {}".format(
#                     threading.current_thread().name
#                 )
#             )
#             request.state.db.close()
#         return response


class AddProcessTimeMiddleware(BaseHTTPMiddleware):
    """Figure out how long it takes for a request to process.

    Arguments:
        BaseHTTPMiddleware {[type]} -- [description]
    """

    # SOURCE: https://github.com/podhmo/individual-sandbox/blob/c666a27f8bacb8a56750c74998d80405b92cb4e8/daily/20191220/example_starlette/04fastapi-jinja2-with-middleware/test_main.py
    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response


app = get_application()


@app.get("/index")
async def hello_world():
    return "hello world"


# app.include_router(
#     log_endpoint.router, tags=["log"], prefix=f"{settings.API_V1_STR}/logs"
# )
# @app.get("/index")
# async def hello_world():
#     return "hello world"

# Multiple RecursionErrors with self-referencing models
# https://github.com/samuelcolvin/pydantic/issues/524
# https://github.com/samuelcolvin/pydantic/issues/531


@app.get(
    "/{settings.API_V1_STR}/logs/{logger_name}",
    response_model=LoggerModel,
    tags=["log"],
)
async def logger_get(logger_name: str):
    LOGGER.debug(f"getting logger {logger_name}")
    rootm = generate_tree()
    lm = get_lm_from_tree(rootm, logger_name)
    if lm is None:
        raise HTTPException(status_code=404, detail=f"Logger {logger_name} not found")
    return lm


@app.patch("/{settings.API_V1_STR}/logs", tags=["log"])
async def logger_patch(loggerpatch: LoggerPatch):
    rootm = generate_tree()
    lm = get_lm_from_tree(rootm, loggerpatch.name)
    LOGGER.debug(f"Actual level of {lm.name} is {lm.level}")
    LOGGER.debug(f"Setting {loggerpatch.name} to {loggerpatch.level}")
    logging.getLogger(loggerpatch.name).setLevel(LOG_LEVELS[loggerpatch.level])
    return loggerpatch


@app.get("/{settings.API_V1_STR}/logs", response_model=LoggerModel, tags=["log"])
async def loggers_list():
    rootm = generate_tree()
    LOGGER.debug(rootm)
    return rootm


@app.get("/", include_in_schema=False)
async def index():
    return RedirectResponse(url="/docs")


@app.post("/predict/image")
async def predict_api(file: UploadFile = File(...)):
    extension = file.filename.split(".")[-1] in ("jpg", "jpeg", "png")
    if not extension:
        return "Image must be jpg or png format!"
    image = read_imagefile(await file.read())
    prediction = predict(image)

    return prediction

@app.post("/dropbox/upload")
async def dropbox_upload(file: UploadFile = File(...)):
    async with aiodbx.AsyncDropboxAPI(settings.DROPBOX_AIODROPBOX_TOKEN) as dbx:
        await dbx.validate()

        LOGGER.info("simulating cerebro download then upload to dropbox ...")
        data = await file.read()
        p = pathlib.Path(file.filename)
        extension = p.suffix.split(".")[-1]
        fname = p.stem
        directory = "/Users/malcolm/dev/bossjones/sandbox/aiopillow/audit"
        async with aiofiles.tempfile.NamedTemporaryFile('wb+') as f:
            LOGGER.info(f"writing to {f.name}")
            await f.write(data)
            await f.flush()
            await f.seek(0)

            filename = f.name
            LOGGER.info(f"os.path.exists(filename) -> {os.path.exists(filename)}")
            LOGGER.info(f"os.path.isfile(filename) -> {os.path.isfile(filename)}")

        path_to_file = await writer.write_file(fname, data, extension, directory)
        path_to_file_api = pathlib.Path(path_to_file).absolute()
        assert path_to_file_api.exists()

        list_of_files_to_upload = [path_to_file]

        # create a coroutine for each link in shared_links
        # run them and print a simple confirmation message when we have a result
        coroutines = [run_upload_to_dropbox(dbx, _file) for _file in list_of_files_to_upload]
        for coro in asyncio.as_completed(coroutines):
            try:
                res = await coro
            # except aiodbx.DropboxAPIError as e:
            #     # this exception is raised when the API returns an error
            #     LOGGER.error('Encountered an error')
            #     LOGGER.error(e)
            # else:
            #     LOGGER.info(f'Processed {res}')
            except Exception as ex:
                print(str(ex))
                exc_type, exc_value, exc_traceback = sys.exc_info()
                LOGGER.error("Error Class: {}".format(str(ex.__class__)))
                output = "[{}] {}: {}".format("UNEXPECTED", type(ex).__name__, ex)
                LOGGER.warning(output)
                LOGGER.error("exc_type: {}".format(exc_type))
                LOGGER.error("exc_value: {}".format(exc_value))
                traceback.print_tb(exc_traceback)
                raise
            else:
                LOGGER.info(f'Processed {res}')

        # once everything is uploaded, finish the upload batch
        # this returns the metadata of all of the uploaded files
        uploaded_files = await dbx.upload_finish()

        # print out some info
        LOGGER.info('\nThe files we just uploaded are:')
        for file in uploaded_files:
            LOGGER.info(file['name'])



        # asyncio.get_event_loop().run_until_complete(main(token, shared_links, log))

    return "data written"


@app.post("/api/covid-symptom-check")
def check_risk(symptom: Symptom):
    return symptom_check.get_risk_level(symptom)


# Instrumentator().instrument(app).expose(app)


if __name__ == "__main__":
    # import os
    HOST = "localhost"
    PORT = int(os.environ.get("PORT", 11267))

    # LOGGER.level("uvicorn")
    LOGGER.add(sys.stderr, filter="uvicorn", level="DEBUG")

    # print(tf.logging._level_names)
    # print(tf.logging.get_verbosity())

    # APP_MODULE_STR = os.environ.get("APP_MODULE")
    APP_MODULE_STR = "aiopillow.web:app"
    app_import_str = f"{APP_MODULE_STR}"
    uvicorn.run(
        "web:app",
        host=HOST,
        port=PORT,
        log_level=settings._USER_LOG_LEVEL.lower(),
        reload=True,
        debug=True,
    )
