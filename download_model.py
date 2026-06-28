"""Download and extract ChromaDB's default ONNX embedding model."""

import os
import tarfile
import urllib.request
from pathlib import Path


def download_model():
    model_name = "all-MiniLM-L6-v2"
    url = (
        "https://chroma-onnx-models.s3.amazonaws.com/"
        f"{model_name}/onnx.tar.gz"
    )
    download_path = Path.home() / ".cache" / "chroma" / "onnx_models" / model_name
    download_path.mkdir(parents=True, exist_ok=True)
    archive_path = download_path / "onnx.tar.gz"

    if (download_path / "onnx").exists():
        print(f"Model already present at {download_path / 'onnx'}")
        return

    print(f"Downloading {url} ...")
    with urllib.request.urlopen(url, timeout=600) as response, open(
        archive_path, "wb"
    ) as out_file:
        out_file.write(response.read())

    print("Extracting model archive...")
    with tarfile.open(archive_path, "r:gz") as tar:
        tar.extractall(path=download_path)

    os.remove(archive_path)
    print(f"Model ready at {download_path}")


if __name__ == "__main__":
    download_model()
