import os

import fastapi
import fastapi.responses
import sqlmodel

import context
import log
import main_shared
import models
import services.corpus
import services.corpus.fs
import services.corpus.keyword
import services.corpus.vector

logger = log.init("app")

# initialize templates dir
templates = fastapi.templating.Jinja2Templates(directory="routers/rag")

app = fastapi.APIRouter(
    tags=["app.rag"],
    dependencies=[fastapi.Depends(main_shared.get_db)],
    responses={404: {"description": "Not found"}},
)

app_version = os.environ["APP_VERSION"]

@app.get("/rag/corpuses", response_class=fastapi.responses.HTMLResponse)
def rag_corpuses(request: fastapi.Request, query: str = "", db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db)):
    """
    """
    logger.info(f"{context.rid_get()} rag corpuses query '{query}'")

    try:
        list_result = services.corpus.list_(db_session=db_session, query=query, offset=0, limit=50)
        corpus_list = list_result.objects
    except Exception as e:
        corpus_list = []
        logger.error(f"{context.rid_get()} rag corpuses query exception '{e}'")

    return templates.TemplateResponse(
        request,
        "corpuses.html",
        {
            "app_name": "Corpuses",
            "app_version": app_version,
            "corpus_list": corpus_list,
            "prompt_text": "search query",
            "query": query,
        }
    )


@app.get("/rag/fs", response_class=fastapi.responses.HTMLResponse)
def rag_fs(request: fastapi.Request, db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db)):
    """
    """
    logger.info(f"{context.rid_get()} rag fs")

    list_result = services.corpus.fs.list_(db_session=db_session, dir="./data/rag")

    return templates.TemplateResponse(
        request,
        "fs.html",
        {
            "app_name": "Dirs",
            "app_version": app_version,
            "corpuses": list_result.corpuses,
        }
    )


@app.get("/rag/ingest", response_class=fastapi.responses.HTMLResponse)
async def rag_ingest(
    background_tasks: fastapi.BackgroundTasks,
    corpus_id: int=0,
    source_dir: str="",
    db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db),
):
    """
    """
    try:
        corpus = services.corpus.get_by_id(db_session=db_session, id=corpus_id)

        if corpus:
            # existing corpus
            logger.info(f"{context.rid_get()} rag ingest corpus_id {corpus_id} source_dir '{source_dir}'")
        else:
            # new corpus
            model_name = "gte-large"
            splitter_name = "semantic"
            corpus_name = source_dir.split("/")[-1]

            corpus = models.Corpus(
                embed_dims=services.corpus.embed_dims(model=model_name),
                embed_model = model_name,
                name=services.corpus.name_encode(corpus=corpus_name, model=model_name, splitter=splitter_name),
                source_dir=source_dir,
            )

            logger.info(f"{context.rid_get()} rag ingest corpus 'new' source_dir '{source_dir}'")

        if corpus.id:
            # update corpus state
            corpus.state = models.corpus.STATE_QUEUED
            db_session.add(corpus)
            db_session.commit()

        background_tasks.add_task(
            services.corpus.ingest,
            db_session=db_session,
            name_encoded=corpus.name,
            source_dir=corpus.source_dir,
            embed_model=services.corpus.embed_model(model=corpus.embed_model),
            embed_dims=corpus.embed_dims,
            splitter=corpus.splitter or splitter_name,
        )
    except Exception as e:
        logger.error(f"{context.rid_get()} rag ingest exception '{e}'")
        return fastapi.responses.RedirectResponse("/rag/fs")

    return fastapi.responses.RedirectResponse("/rag/corpuses")


@app.get("/rag/query", response_class=fastapi.responses.HTMLResponse)
def rag_query(
    request: fastapi.Request,
    corpus: str = "",  # full corpus name
    mode: str = "retrieve",
    query: str = "",
    limit: int = 10,
    db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db),
):
    list_result = services.corpus.list_(db_session=db_session, query="", offset=0, limit=10)
    corpus_list = [object.name for object in list_result.objects]

    modes = ["augment", "keyword", "retrieve"]
    models = services.corpus.embed_models()

    query_nodes = []
    query_response = ""
    query_ok = ""
    query_error = ""

    if corpus and query:
        logger.info(f"{context.rid_get()} rag retrieve corpus '{corpus}' mode '{mode}' query '{query}'")

        try:
            if mode == "augment":
                augment_result = services.corpus.vector.search_augment(
                    db_session=db_session,
                    name_encoded=corpus,
                    query=query,
                )

                if augment_result.code != 0:
                    query_error = f"error: {augment_result.errors[0]}"
                else:
                    query_response = augment_result.response
                    query_ok = f"response generated in {round(augment_result.msec, 0)} msec"
            elif mode == "retrieve":
                retrieve_result = services.corpus.vector.search_retrieve(
                    db_session=db_session,
                    name_encoded=corpus,
                    query=query,
                    limit=limit,
                )

                if retrieve_result.code != 0:
                    query_error = f"error: {retrieve_result.errors[0]}"
                else:
                    query_nodes = retrieve_result.nodes
                    query_ok = f"{len(query_nodes)} results in {round(retrieve_result.msec, 0)} msec"

                    # todo
                    # services.corpus.text_ratios(texts=[node.text for node in nodes])
            elif mode == "keyword":
                retrieve_result = services.corpus.keyword.search_retrieve(
                    db_session=db_session,
                    name_encoded=corpus,
                    query=query,
                    limit=limit,
                )

                if retrieve_result.code != 0:
                    query_error = f"error: {retrieve_result.errors[0]}"
                else:
                    query_nodes = retrieve_result.nodes
                    query_ok = f"{len(query_nodes)} results in {round(retrieve_result.msec, 0)} msec"

        except Exception as e:
            query_error = f"exception: {e}"
    else:
        logger.info(f"{context.rid_get()} rag retrieve index")

    return templates.TemplateResponse(
        request,
        "query.html",
        {
            "app_name": "Rag",
            "app_version": app_version,
            "corpus": corpus,
            "corpus_list": corpus_list,
            "mode": mode,
            "models": models,
            "modes": modes,
            "prompt_text": "ask a question",
            "query": query,
            "query_error": query_error,
            "query_ok": query_ok,
            "query_nodes": query_nodes,
            "query_response": query_response,
        }
    )
