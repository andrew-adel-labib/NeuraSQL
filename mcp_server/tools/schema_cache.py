import os
import json
import hashlib
from typing import Dict, Any


BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

CACHE_DIR = os.path.join(
    BASE_DIR,
    "../cache"
)

os.makedirs(
    CACHE_DIR,
    exist_ok=True
)


def generate_schema_hash(
    schema: Dict
) -> str:
    """
    Stable hash for semantic model
    """

    schema_str = json.dumps(
        schema,
        sort_keys=True
    )

    return hashlib.md5(
        schema_str.encode("utf-8")
    ).hexdigest()


def generate_query_hash(
    query: str
) -> str:
    """
    Stable hash for:
    - query
    - provider
    - pipeline stage
    """

    return hashlib.md5(
        query.lower().strip().encode(
            "utf-8"
        )
    ).hexdigest()


def get_schema_cache_path(
    schema_hash: str
):
    return os.path.join(
        CACHE_DIR,
        f"schema_{schema_hash}.json"
    )


def get_query_cache_path(
    query_hash: str
):
    return os.path.join(
        CACHE_DIR,
        f"query_{query_hash}.json"
    )


def load_cached_schema(
    schema: Dict
):
    schema_hash = generate_schema_hash(
        schema
    )

    path = get_schema_cache_path(
        schema_hash
    )

    if os.path.exists(path):
        with open(
            path,
            "r",
            encoding="utf-8"
        ) as f:
            return json.load(f)

    return None


def save_cached_schema(
    schema: Dict,
    processed_schema: Dict
):
    schema_hash = generate_schema_hash(
        schema
    )

    path = get_schema_cache_path(
        schema_hash
    )

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            processed_schema,
            f,
            indent=2,
            ensure_ascii=False
        )


def load_cached_query(
    query_key: str
):
    """
    query_key format examples:

    rewrite::claude::sales last year
    rewrite::openai::sales last year
    rewrite::groq::sales last year

    semantic::claude::...
    rerank::openai::...
    full_pipeline::groq::...
    """

    query_hash = generate_query_hash(
        query_key
    )

    path = get_query_cache_path(
        query_hash
    )

    if os.path.exists(path):
        try:
            with open(
                path,
                "r",
                encoding="utf-8"
            ) as f:
                return json.load(f)

        except Exception:
            return None

    return None


def save_cached_query(
    query_key: str,
    result: Dict[str, Any]
):
    """
    Provider-aware query cache
    """

    query_hash = generate_query_hash(
        query_key
    )

    path = get_query_cache_path(
        query_hash
    )

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            result,
            f,
            indent=2,
            ensure_ascii=False
        )


def clear_cache():
    """
    Deletes all cache files
    """

    for file in os.listdir(
        CACHE_DIR
    ):
        path = os.path.join(
            CACHE_DIR,
            file
        )

        if os.path.isfile(path):
            os.remove(path)


def clear_provider_cache(
    provider: str
):
    """
    Deletes cache for a specific provider:
    - claude
    - openai
    - groq
    """

    for file in os.listdir(
        CACHE_DIR
    ):
        path = os.path.join(
            CACHE_DIR,
            file
        )

        if not os.path.isfile(path):
            continue

        try:
            with open(
                path,
                "r",
                encoding="utf-8"
            ) as f:
                data = json.load(f)

            if data.get(
                "model_provider"
            ) == provider:
                os.remove(path)

        except Exception:
            continue


def cache_stats():
    """
    Returns:
    - total files
    - total size
    """

    total_files = 0
    total_size = 0

    for file in os.listdir(
        CACHE_DIR
    ):
        path = os.path.join(
            CACHE_DIR,
            file
        )

        if os.path.isfile(path):
            total_files += 1
            total_size += os.path.getsize(
                path
            )

    return {
        "cache_dir": CACHE_DIR,
        "total_files": total_files,
        "total_size_mb": round(
            total_size / (1024 * 1024),
            2
        )
    }