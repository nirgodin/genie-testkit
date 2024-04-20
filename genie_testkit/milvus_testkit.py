from typing import Optional

from pymilvus import MilvusClient as MilvusSyncClient, FieldSchema, DataType, CollectionSchema, connections
from pymilvus.milvus_client import IndexParams


TRACK_NAMES_EMBEDDINGS_COLLECTION_NAME = "track_names_embeddings"
EMBEDDINGS_FIELD_NAME = "embeddings"


class MilvusTestkit:
    def __init__(self, uri: str = "http://localhost:19530", token: str = ""):
        self.uri = uri
        self.token = token
        self._client: Optional[MilvusSyncClient] = None

    def __enter__(self) -> "MilvusTestkit":
        self._client = MilvusSyncClient(uri=self.uri)
        self._initialize_embeddings_collection()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self._client.drop_collection(TRACK_NAMES_EMBEDDINGS_COLLECTION_NAME)
        self._client = None
        connections.disconnect("default")

    def _initialize_embeddings_collection(self) -> None:
        connections.connect(uri=self.uri)
        schema = self._get_collection_schema()
        self._client.create_collection(
            collection_name=TRACK_NAMES_EMBEDDINGS_COLLECTION_NAME,
            schema=schema
        )
        self._client.create_index(
            collection_name=TRACK_NAMES_EMBEDDINGS_COLLECTION_NAME,
            index_params=IndexParams(field_name=EMBEDDINGS_FIELD_NAME)
        )
        self._client.load_collection(TRACK_NAMES_EMBEDDINGS_COLLECTION_NAME)

    @staticmethod
    def _get_collection_schema() -> CollectionSchema:
        id_field = FieldSchema(
            name="id",
            dtype=DataType.VARCHAR,
            max_length=22,
            is_primary=True
        )
        name_field = FieldSchema(
            name="name",
            dtype=DataType.VARCHAR,
            max_length=220,
        )
        embeddings_field = FieldSchema(
            name=EMBEDDINGS_FIELD_NAME,
            dtype=DataType.FLOAT_VECTOR,
            dim=1536,
        )

        return CollectionSchema(
            fields=[id_field, name_field, embeddings_field],
            auto_id=False,
            enable_dynamic_field=True
        )
