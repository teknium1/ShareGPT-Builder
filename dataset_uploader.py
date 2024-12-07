import os
import json
import tempfile
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pyarrow as pa
import pyarrow.parquet as pq
from huggingface_hub import CommitScheduler
from huggingface_hub.hf_api import HfApi

###################################
# Parquet scheduler               #
# Uploads data in parquet format  #
###################################


class ParquetScheduler(CommitScheduler):
    """
    Usage: configure the scheduler with a repo id. Once started, you can add data to be uploaded to the Hub. 1 `.append`
    call will result in 1 row in your final dataset.

    ```py
    # Start scheduler
    >>> scheduler = ParquetScheduler(repo_id="my-parquet-dataset")

    # Append some data to be uploaded
    >>> scheduler.append({...})
    >>> scheduler.append({...})
    >>> scheduler.append({...})
    ```

    The scheduler will automatically infer the schema from the data it pushes.
    Optionally, you can manually set the schema yourself:

    ```py
    >>> scheduler = ParquetScheduler(
    ...     repo_id="my-parquet-dataset",
    ...     schema={
    ...         "prompt": {"_type": "Value", "dtype": "string"},
    ...         "negative_prompt": {"_type": "Value", "dtype": "string"},
    ...         "guidance_scale": {"_type": "Value", "dtype": "int64"},
    ...         "image": {"_type": "Image"},
    ...     },
    ... )

    See https://huggingface.co/docs/datasets/main/en/package_reference/main_classes#datasets.Value for the list of
    possible values.
    """

    def __init__(
        self,
        *,
        repo_id: str,
        schema: Optional[Dict[str, Dict[str, str]]] = None,
        every: Union[int, float] = 5,
        path_in_repo: Optional[str] = "data",
        repo_type: Optional[str] = "dataset",
        revision: Optional[str] = None,
        private: bool = False,
        token: Optional[str] = None,
        allow_patterns: Union[List[str], str, None] = None,
        ignore_patterns: Union[List[str], str, None] = None,
        hf_api: Optional[HfApi] = None,
    ) -> None:
        super().__init__(
            repo_id=repo_id,
            folder_path="dummy",  # not used by the scheduler
            every=every,
            path_in_repo=path_in_repo,
            repo_type=repo_type,
            revision=revision,
            private=private,
            token=token,
            allow_patterns=allow_patterns,
            ignore_patterns=ignore_patterns,
            hf_api=hf_api,
        )

        self._rows: List[Dict[str, Any]] = []
        self._schema = schema

    def append(self, row: Dict[str, Any]) -> None:
        """Add a new item to be uploaded."""
        with self.lock:
            self._rows.append(row)

    def push_to_hub(self):
        # Check for new rows to push
        with self.lock:
            rows = self._rows
            self._rows = []
        if not rows:
            return
        print(f"Got {len(rows)} item(s) to commit.")

        # Load images + create 'features' config for datasets library
        schema: Dict[str, Dict] = self._schema or {}
        path_to_cleanup: List[Path] = []
        for row in rows:
            for key, value in row.items():
                # Infer schema (for `datasets` library)
                if key not in schema:
                    schema[key] = _infer_schema(key, value)

                # Load binary files if necessary
                if schema[key]["_type"] in ("Image", "Audio"):
                    # It's an image or audio: we load the bytes and remember to cleanup the file
                    file_path = Path(value)
                    if file_path.is_file():
                        row[key] = {
                            "path": file_path.name,
                            "bytes": file_path.read_bytes(),
                        }
                        path_to_cleanup.append(file_path)

        # Complete rows if needed
        for row in rows:
            for feature in schema:
                if feature not in row:
                    row[feature] = None

        # Export items to Arrow format
        table = pa.Table.from_pylist(rows)

        # Add metadata (used by datasets library)
        table = table.replace_schema_metadata(
            {"huggingface": json.dumps({"info": {"features": schema}})}
        )

        # Write to parquet file
        archive_file = tempfile.NamedTemporaryFile(delete=False)
        pq.write_table(table, archive_file.name)
        archive_file.close()

        # Upload
        self.api.upload_file(
            repo_id=self.repo_id,
            repo_type=self.repo_type,
            revision=self.revision,
            path_in_repo=f"{uuid.uuid4()}.parquet",
            path_or_fileobj=archive_file.name,
        )
        print("Commit completed.")

        # Cleanup
        os.unlink(archive_file.name)
        for path in path_to_cleanup:
            path.unlink(missing_ok=True)


def _infer_schema(key: str, value: Any) -> Dict[str, str]:
    """
    Infer schema for the `datasets` library.

    See https://huggingface.co/docs/datasets/main/en/package_reference/main_classes#datasets.Value.
    """
    # In short any column_name in the dataset has any of these keywords
    # the column will be inferred into the correct column type accordingly
    if "image" in key:
        return {"_type": "Image"}
    if "audio" in key:
        return {"_type": "Audio"}
    if isinstance(value, int):
        return {"_type": "Value", "dtype": "int64"}
    if isinstance(value, float):
        return {"_type": "Value", "dtype": "float64"}
    if isinstance(value, bool):
        return {"_type": "Value", "dtype": "bool"}
    if isinstance(value, bytes):
        return {"_type": "Value", "dtype": "binary"}
    # Otherwise in last resort => convert it to a string
    return {"_type": "Value", "dtype": "string"}
