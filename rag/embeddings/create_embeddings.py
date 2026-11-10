"""
Embedding Generation Stage for NxGen Tech Academy Knowledge Base
================================================================
This script generates vector embeddings for chunks created during the chunking stage.

Model: all-MiniLM-L6-v2 (SentenceTransformers)
Embedding Dimensions: 384
"""

import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer


MODEL_NAME = "all-MiniLM-L6-v2"
EXPECTED_DIMENSION = 384


def find_chunks_file(workspace_root: Path) -> Path:
    """Locates chunks.json across standard workspace locations."""
    candidate_paths = [
        workspace_root / "rag" / "chunks" / "chunks.json",
        workspace_root / "chunks" / "chunks.json",
        Path(__file__).resolve().parent.parent / "chunks" / "chunks.json",
        Path(__file__).resolve().parent / "chunks.json"
    ]
    for p in candidate_paths:
        if p.is_file():
            return p.resolve()
    
    raise FileNotFoundError(
        f"Could not find chunks.json in any expected location: {[str(p) for p in candidate_paths]}"
    )


def load_chunks(chunks_file: Path) -> List[Dict[str, Any]]:
    """Loads and validates chunks from JSON file."""
    if not chunks_file.exists():
        raise FileNotFoundError(f"Chunks file not found at {chunks_file}")

    with open(chunks_file, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    if not isinstance(chunks, list) or len(chunks) == 0:
        raise ValueError(f"Chunks file at {chunks_file} is empty or not a valid JSON list.")

    return chunks


def generate_embeddings(
    chunks: List[Dict[str, Any]],
    model_name: str = MODEL_NAME
) -> Tuple[np.ndarray, List[Dict[str, Any]]]:
    """
    Extracts text from chunks and generates embeddings using SentenceTransformer.
    Returns (embeddings_array, metadata_list).
    """
    print(f"Loading SentenceTransformer model: '{model_name}'...")
    model = SentenceTransformer(model_name)

    print(f"Extracting text from {len(chunks)} chunks...")
    texts = [chunk["text"] for chunk in chunks]
    metadata_list = [
        {
            "chunk_id": idx,
            "course": chunk["metadata"]["course"],
            "section": chunk["metadata"]["section"],
            "source_file": chunk["metadata"]["source_file"],
            "text_length": len(chunk["text"])
        }
        for idx, chunk in enumerate(chunks)
    ]

    print(f"Generating embeddings for {len(texts)} chunks...")
    embeddings = model.encode(
        texts,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    if embeddings.shape[0] != len(chunks):
        raise ValueError(f"Expected {len(chunks)} embeddings, got {embeddings.shape[0]}")
    if embeddings.shape[1] != EXPECTED_DIMENSION:
        raise ValueError(f"Expected embedding dimension {EXPECTED_DIMENSION}, got {embeddings.shape[1]}")

    return embeddings, metadata_list


def save_embeddings(
    embeddings: np.ndarray,
    metadata_list: List[Dict[str, Any]],
    output_dir: Path
) -> Tuple[Path, Path]:
    """
    Saves embeddings as a compact NumPy binary file and metadata as JSON.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    npy_path = output_dir / "embeddings.npy"
    meta_path = output_dir / "embeddings_metadata.json"

    np.save(npy_path, embeddings)

    metadata_payload = {
        "model_name": MODEL_NAME,
        "embedding_dimension": int(embeddings.shape[1]),
        "total_embeddings": int(embeddings.shape[0]),
        "chunks": metadata_list
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata_payload, f, indent=2, ensure_ascii=False)

    return npy_path, meta_path


def run_embedding_pipeline():
    workspace_root = Path(__file__).resolve().parent.parent.parent
    output_dir = Path(__file__).resolve().parent

    print("=" * 65)
    print("NxGen Tech Academy - Knowledge-Base Embedding Stage")
    print("=" * 65)
    
    chunks_file = find_chunks_file(workspace_root)
    print(f"Loaded chunks from:    {chunks_file}")
    chunks = load_chunks(chunks_file)
    print(f"Total chunks found:    {len(chunks)}")
    print("-" * 65)

    embeddings, metadata_list = generate_embeddings(chunks, MODEL_NAME)
    npy_path, meta_path = save_embeddings(embeddings, metadata_list, output_dir)

    print("-" * 65)
    print("Embedding Generation Summary:")
    print(f"  • Model Used:            {MODEL_NAME}")
    print(f"  • Number of Embeddings:  {embeddings.shape[0]}")
    print(f"  • Embedding Dimension:   {embeddings.shape[1]} (Expected: {EXPECTED_DIMENSION})")
    print(f"  • Embeddings Array File: {npy_path}")
    print(f"  • Metadata Mapping File: {meta_path}")
    print("=" * 65)
    print("Embedding stage completed successfully!")


if __name__ == "__main__":
    run_embedding_pipeline()
