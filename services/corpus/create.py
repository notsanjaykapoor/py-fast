import datetime
import os

import sqlmodel

import models
import services.corpus

def create(
    db_session: sqlmodel.Session,
    model: str,
    epoch: int,
    org_id: int,
    source_uri: str,
    state: str,
    params: dict,
) -> models.Corpus:
    """
    Create database corpus object.
    """
    source_name, _, _ = services.corpus.source_uri_parse(source_uri=source_uri)

    corpus_name = services.corpus.name_generate(
        corpus=source_name,
        strip=os.environ.get("APP_FS_STRIP", ""),
    )

    corpus = models.Corpus(
        docs_count=params.get("docs_count") or 0,
        epoch=epoch,
        files_count=params.get("files_count") or 0,
        fingerprint=params.get("fingerprint") or "",
        meta=params.get("meta") or {},
        model_dims=services.corpus.model_dims(model=model),
        model_name=model,
        name=corpus_name,
        nodes_count=params.get("nodes_count") or 0,
        org_id=org_id,
        source_uri=source_uri,
        state=state,
        updated_at=datetime.datetime.now(datetime.timezone.utc)
    )

    db_session.add(corpus)
    db_session.commit()

    return corpus