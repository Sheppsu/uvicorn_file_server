from server import (
    app,
    router,
    RequestInfo,
    Response,
    JsonResponse,
    StaticFileResponse
)
from sql import Database

import re
import os
import secrets
import logging
import mimetypes
from dotenv import load_dotenv


load_dotenv()


_log = logging.getLogger(__name__)
API_KEY = os.getenv("API_KEY")
db = Database()

formdata_re = re.compile(r"multipart/form-data;\s?boundary=([a-f0-9\-]*)", re.IGNORECASE)
disposition_re = re.compile(r"Content-Disposition: form-data;\s?name=\".*\";\s?filename=\"(.*)\"")
content_type_re = re.compile(r"Content-Type: (\S*)")


async def download_file(req: RequestInfo, path):
    await req.read_body()
    content = req.body.split(b"\n")

    match = re.match(formdata_re, req.headers["content-type"].decode())
    if match is None:
        return JsonResponse(400, {"error": "multipart/form-data is required"})
    boundary = match[1].encode()
    content_length = int(req.headers['content-length'].decode())
    if content_length < 1:
        return JsonResponse(400, {"error": "no content to read"})

    line = content[0]
    content_length -= len(line)
    if boundary not in line:
        return JsonResponse(400, {"error": "first line does not contain boundary"})
    if content_length < 1:
        return JsonResponse(400, {"error": "form data is incomplete"})

    line = content[1]
    content_length -= len(line)
    match = re.match(disposition_re, line.decode())
    if match is None:
        return JsonResponse(400, {"error": "invalid content-disposition in form data"})
    filename = match[1]
    file_ext = filename.split(".")[-1]
    if content_length < 1:
        return JsonResponse(400, {"error": "form data is incomplete"})

    line = content[2]
    content_length -= len(line)
    match = re.match(content_type_re, line.decode())
    if match is None:
        return JsonResponse(400, {"error": "invalid content-type in form data"})
    content_type = match[1]
    if content_length < 1:
        return JsonResponse(400, {"error": "form data is incomplete"})

    content_length -= len(content[3])
    boundary_found = False
    new_path = path+"."+file_ext
    with open(new_path, "wb") as f:
        i = 0
        while content_length > 0:
            line = content[4+i]
            i += 1
            content_length -= len(line)
            if boundary in line:
                boundary_found = True
                break
            f.write(line+b"\n" if 5+i != len(content) else b"")
    if not boundary_found:
        return JsonResponse(400, {"error": "form data is incomplete"})
    return new_path, content_type


@router.route("/upload", method="POST")
async def upload(req: RequestInfo):
    if "api-key" not in req.headers:
        return JsonResponse(400, {"error": "must specify an api key"})
    if req.headers["api-key"].decode() != API_KEY:
        return JsonResponse(400, {"error": "invalid api key"})
    result = await download_file(req, "files/"+secrets.token_urlsafe())
    if isinstance(result, tuple):
        path, content_type = result
        code = secrets.token_urlsafe(8)
        db.add_file(code, os.path.split(path)[-1], content_type)
        return JsonResponse(200, {"url": "https://media.sheppsu.me/view?n=%s" % code})
    return result


@router.route("/status")
async def status(req: RequestInfo):
    return Response(200, body=b"OK")


@router.route("/view", regex=True)
async def view(req: RequestInfo):
    filedata = db.get_file(req.query.get("n", ""))
    if not filedata:
        return Response(404)

    mime = filedata[1]
    with open("view.html") as f:
        return Response(
            200,
            body=f.read().replace("{{ mimetype }}", mime).encode("utf-8")
        )


@router.route("/static/(?P<file>\S*)", regex=True)
async def static_file(req: RequestInfo, file):
    if not os.path.exists(f"static/{file}"):
        return Response(404)

    mime = mimetypes.guess_type(file)[0]
    headers = {} if mime is None else {"Content-Type": mime}
    with open(f"static/{file}", "rb") as f:
        return Response(200, body=f.read(), headers=headers)


@router.route(r"/(?P<code>\S*)", regex=True)
async def query(req: RequestInfo, code):
    if "." in code:
        code = ".".join(code.split(".")[:-1])
    filedata = db.get_file(code)
    if not filedata:
        return Response(404)
    db.update_file_stats(code)
    return StaticFileResponse(200, f"files/{filedata[0]}", headers={"Content-Type": filedata[1]})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("run:app", port=8726, ssl_keyfile="key.pem", ssl_certfile="cert.pem")
