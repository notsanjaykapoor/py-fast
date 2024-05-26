import os

import fastapi
import fastapi.responses
import sqlmodel

import context
import log
import models
import main_shared
import services.work_queue

logger = log.init("app")

# initialize templates dir
templates = fastapi.templating.Jinja2Templates(directory="routers")

app = fastapi.APIRouter(
    tags=["app.rag"],
    dependencies=[fastapi.Depends(main_shared.get_db)],
    responses={404: {"description": "Not found"}},
)

app_version = os.environ["APP_VERSION"]

@app.get("/admin")
def admin_home():
    return fastapi.responses.RedirectResponse("/admin/workq")


@app.get("/admin/corpus/ingest", response_class=fastapi.responses.HTMLResponse)
async def admin_corpus_ingest(
    corpus_id: int=0,
    source_uri: str="",
    db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db),
):
    """
    """
    try:
        corpus = services.corpus.init(
            db_session=db_session,
            corpus_id=corpus_id,
            source_uri=source_uri,
            model=services.corpus.utils.MODEL_NAME_DEFAULT,
            splitter=services.corpus.utils.SPLITTER_NAME_DEFAULT,
        )

        logger.info(f"{context.rid_get()} admin corpus '{corpus.name}' id {corpus.id} ingest")

        corpus.state = models.corpus.STATE_QUEUED

        db_session.add(corpus)
        db_session.commit()

        services.work_queue.add(
            db_session=db_session,
            data={
                "corpus_id": corpus.id
            },
            msg="ingest",
            queue=models.work_queue.QUEUE_CORPUS_INGEST,
            partition=services.work_queue.partition(
                buckets=models.work_queue.QUEUE_CORPUS_INGEST_PARTITIONS,
                id=corpus.id,
            ),
        )

        # background_tasks.add_task(
        #     services.corpus.ingest,
        #     db_session=db_session,
        #     corpus_id=corpus.id
        # )
    except Exception as e:
        logger.error(f"{context.rid_get()} admin corpus ingest exception '{e}'")
        return fastapi.responses.RedirectResponse("/admin/fs")

    return fastapi.responses.RedirectResponse(f"/admin/corpus/{corpus.id}")


@app.get("/admin/corpus", response_class=fastapi.responses.HTMLResponse)
def admin_corpus_list(
    request: fastapi.Request,
    query: str = "",
    offset: int=0,
    limit: int=50,
    db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db),
):
    """
    """
    if "HX-Request" in request.headers:
        htmx_request = 1
    else:
        htmx_request = 0

    logger.info(f"{context.rid_get()} rag corpus htmx {htmx_request} query '{query}'")

    try:
        list_result = services.corpus.list(
            db_session=db_session,
            query=query,
            offset=offset,
            limit=limit,
        )
        corpus_list = list_result.objects
        query_code = 0
        query_result = f"{list_result.total} results"
    except Exception as e:
        corpus_list = []
        query_code = 400
        query_result = f"exception {e}"
        logger.error(f"{context.rid_get()} rag corpus query exception '{e}'")

    if htmx_request == 1:
        template = "admin/corpus/list_table.html"
    else:
        template = "admin/corpus/list.html"

    response = templates.TemplateResponse(
        request,
        template,
        {
            "app_name": "Corpus",
            "app_version": app_version,
            "corpus_list": corpus_list,
            "prompt_text": "search",
            "query": query,
            "query_code": query_code,
            "query_result": query_result,
        }
    )

    if htmx_request == 1:
        response.headers["HX-Push-Url"] = f"{request.get('path')}?query={query}"

    return response


@app.get("/admin/corpus/{corpus_id}", response_class=fastapi.responses.HTMLResponse)
def admin_corpus_show(request: fastapi.Request, corpus_id: int, db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db)):
    """
    """
    logger.info(f"{context.rid_get()} rag corpus show {corpus_id}")

    try:
        corpus = services.corpus.get_by_id(db_session=db_session, id=corpus_id)
    except Exception as e:
        logger.error(f"{context.rid_get()} rag corpus show exception '{e}'")

    return templates.TemplateResponse(
        request,
        "admin/corpus/show.html",
        {
            "app_name": "Corpus",
            "app_version": app_version,
            "corpus": corpus,
        }
    )


@app.get("/admin/fs", response_class=fastapi.responses.HTMLResponse)
def admin_fs_list(
    request: fastapi.Request,
    query: str="",
    offset: int=0,
    limit: int=50,
    db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db),
):
    """
    """
    if "HX-Request" in request.headers:
        htmx_request = 1
    else:
        htmx_request = 0

    logger.info(f"{context.rid_get()} rag fs htmx {htmx_request} query '{query}'")

    try:
        list_result = services.corpus.fs.list(
            db_session=db_session,
            local_dir=os.environ.get("APP_FS_ROOT"),
            query=query,
            offset=offset,
            limit=limit,
        )
        corpus_map = list_result.corpus_map
        source_uris = list_result.source_uris
        query_code = 0
        query_result = f"{len(source_uris)} results"
    except Exception as e:
        corpus_map = {}
        source_uris = []
        query_code = 400
        query_result = f"exception {e}"
        logger.error(f"{context.rid_get()} rag fs exception '{e}'")

    if htmx_request == 1:
        template = "admin/fs/list_table.html"
    else:
        template = "admin/fs/list.html"

    response = templates.TemplateResponse(
        request,
        template,
        {
            "app_name": "Files",
            "app_version": app_version,
            "corpus_map": corpus_map,
            "query": query,
            "prompt_text": "search",
            "source_uris": source_uris,
            "query_code": query_code,
            "query_result": query_result,
        }
    )

    if htmx_request == 1:
        response.headers["HX-Push-Url"] = f"{request.get('path')}?query={query}"

    return response


@app.get("/admin/workq", response_class=fastapi.responses.HTMLResponse)
def admin_workq_list(
    request: fastapi.Request,
    query: str="",
    offset: int=0,
    limit: int=50,
    db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db),
):
    """
    """
    if "HX-Request" in request.headers:
        htmx_request = 1
    else:
        htmx_request = 0

    logger.info(f"{context.rid_get()} admin workq htmx {htmx_request} query '{query}'")

    try:
        list_result = services.work_queue.list(db_session=db_session, query=query, offset=offset, limit=limit)
        work_objects = list_result.objects
        query_code = 0
        query_result = f"{list_result.total} results"
    except Exception as e:
        work_objects = []
        query_code = 400
        query_result = f"exception {e}"
        logger.error(f"{context.rid_get()} admin workq exception '{e}'")

    if htmx_request == 1:
        template = "admin/workq/list_table.html"
    else:
        template = "admin/workq/list.html"

    response = templates.TemplateResponse(
        request,
        template,
        {
            "app_name": "WorkQ",
            "app_version": app_version,
            "prompt_text": "search",
            "query": query,
            "work_objects": work_objects,
            "query_code": query_code,
            "query_result": query_result,
        }
    )

    if htmx_request == 1:
        response.headers["HX-Push-Url"] = f"{request.get('path')}?query={query}"

    return response
