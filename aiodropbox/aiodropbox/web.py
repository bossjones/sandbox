import sys
import logging
import os
from pathlib import Path
import subprocess
import time

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
from tensorflow.keras.applications.imagenet_utils import decode_predictions
import uvicorn

from aiodropbox import settings
from aiodropbox.components import predict, read_imagefile
from aiodropbox.components.prediction import symptom_check
from aiodropbox.schema import Symptom

app_desc = """<h2>Try this app by uploading any image with `predict/image`</h2>
<h2>Try Covid symptom checker api - it is just a learning app demo</h2>
<br>by Aniket Maurya"""


# SOURCE: https://blog.hipolabs.com/remote-debugging-with-vscode-docker-and-pico-fde11f0e5f1c
def start_debugger():
    parent_pid = os.getppid()
    # cmd = "ps aux | grep %s | awk '{print $2}'" % "ULTRON_ENABLE_WEB"
    cmd = "ps aux | grep 'python aiodropbox/web.py' | awk '{print $2}' | head -1"
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


from aiodropbox.dbx_logger import get_logger  # noqa: E402

LOGGER = get_logger(__name__, provider="Web", level=logging.DEBUG)

FASTAPI_LOGGER = logging.getLogger("fastapi")
FASTAPI_LOGGER.setLevel(logging.DEBUG)

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
    app = FastAPI(title="aiodropbox Web Server", description=app_desc)

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
    Instrumentator().instrument(app).expose(app)

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


@app.post("/api/covid-symptom-check")
def check_risk(symptom: Symptom):
    return symptom_check.get_risk_level(symptom)


if __name__ == "__main__":
    # import os
    HOST = "localhost"
    PORT = int(os.environ.get("PORT", 11267))

    # LOGGER.level("uvicorn")
    LOGGER.add(sys.stderr, filter="uvicorn", level="DEBUG")

    # APP_MODULE_STR = os.environ.get("APP_MODULE")
    APP_MODULE_STR = "aiodropbox.web:app"
    app_import_str = f"{APP_MODULE_STR}"
    uvicorn.run(
        "web:app",
        host=HOST,
        port=PORT,
        log_level=settings._USER_LOG_LEVEL.lower(),
        reload=True,
        debug=True,
    )
