"""
RAG Knowledge Base & Embeddings Ingestion Script
=================================================
Loads pre-computed 384-dimensional dense vector embeddings (`embeddings.npy`)
and corresponding knowledge-base chunks (`chunks.json`) into the existing
PostgreSQL `rag_documents` table using `pgvector` and `psycopg2`.

Safety Features:
- Dynamic chunk count and dimension (384) pre-validation.
- Strict 1-to-1 sequential mapping preservation (chunk[i] <-> embedding[i]).
- Pre-insertion table inspection (prevents accidental duplicate insertion).
- Full ACID transaction management with automatic rollback on error.
- Secure environment-variable based PostgreSQL credential handling.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any, Tuple
import numpy as np
import psycopg2
from psycopg2.extras import execute_values


# Terminal output encoding safety
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


EXPECTED_DIMENSION = 384
TABLE_NAME = "rag_documents"


def resolve_file_paths() -> Tuple[Path, Path]:
    """Locates chunks.json and embeddings.npy relative to this script."""
    current_dir = Path(__file__).resolve().parent

    chunks_candidates = [
        current_dir / "chunks" / "chunks.json",
        current_dir.parent / "rag" / "chunks" / "chunks.json",
        current_dir / "chunks.json",
    ]
    chunks_path = None
    for p in chunks_candidates:
        if p.is_file():
            chunks_path = p.resolve()
            break

    embeddings_candidates = [
        current_dir / "embeddings" / "embeddings.npy",
        current_dir.parent / "rag" / "embeddings" / "embeddings.npy",
        current_dir / "embeddings.npy",
    ]
    embeddings_path = None
    for p in embeddings_candidates:
        if p.is_file():
            embeddings_path = p.resolve()
            break

    if not chunks_path:
        raise FileNotFoundError(f"Could not locate chunks.json in: {[str(p) for p in chunks_candidates]}")
    if not embeddings_path:
        raise FileNotFoundError(f"Could not locate embeddings.npy in: {[str(p) for p in embeddings_candidates]}")

    return chunks_path, embeddings_path


def load_and_validate_data() -> Tuple[List[Dict[str, Any]], np.ndarray]:
    """Loads chunks and embeddings with rigorous consistency and shape validation."""
    chunks_path, embeddings_path = resolve_file_paths()
    print(f"Loading chunks from:     {chunks_path}")
    print(f"Loading embeddings from: {embeddings_path}")

    # 1. Load Chunks
    with open(chunks_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    if not isinstance(chunks, list):
        raise ValueError(f"Expected chunks.json to contain a JSON array, got {type(chunks).__name__}")

    # 2. Load Embeddings
    embeddings = np.load(embeddings_path)

    # 3. Validate Counts and Dimensions
    total_chunks = len(chunks)
    total_embeddings = embeddings.shape[0]

    print(f"Total Chunks Found:      {total_chunks}")
    print(f"Total Embeddings Found:  {total_embeddings}")
    print(f"Embeddings Matrix Shape: {embeddings.shape}")

    if total_chunks == 0:
        raise ValueError("Validation Error: chunks.json contains 0 chunks.")

    if total_chunks != total_embeddings:
        raise ValueError(
            f"Validation Error: Mismatch between chunks count ({total_chunks}) and embeddings count ({total_embeddings})."
        )

    if embeddings.shape != (total_chunks, EXPECTED_DIMENSION):
        raise ValueError(
            f"Validation Error: Expected embedding shape ({total_chunks}, {EXPECTED_DIMENSION}), "
            f"but found {embeddings.shape}."
        )

    # Verify no NaN or Inf in vectors
    if np.isnan(embeddings).any():
        raise ValueError("Validation Error: Found NaN values in embedding vectors.")
    if np.isinf(embeddings).any():
        raise ValueError("Validation Error: Found infinite values in embedding vectors.")

    return chunks, embeddings


def get_db_connection():
    """Establishes connection to PostgreSQL using DATABASE_URL or discrete environment variables."""
    # Attempt to load from Backend/.env if DATABASE_URL is not already set in environment
    if not os.getenv("DATABASE_URL"):
        parent_dir = Path(__file__).resolve().parent.parent
        candidates = [
            parent_dir / "Backend" / ".env",
            parent_dir / "NxGenTechAcademy" / "Backend" / ".env",
        ]
        for backend_env in candidates:
            if backend_env.is_file():
                try:
                    from dotenv import load_dotenv
                    load_dotenv(backend_env, override=False)
                    break
                except ImportError:
                    pass

    database_url = os.getenv("DATABASE_URL")
    if database_url:
        print("\nConnecting to PostgreSQL via DATABASE_URL (Neon / Cloud):")
        try:
            from urllib.parse import urlparse
            parsed = urlparse(database_url)
            print(f"  Host:     {parsed.hostname}")
            print(f"  Port:     {parsed.port or 5432}")
            print(f"  Database: {parsed.path.lstrip('/')}")
        except Exception:
            pass

        try:
            conn = psycopg2.connect(database_url, connect_timeout=15)
            return conn
        except Exception as e:
            print(f"\n[ERROR] Failed to connect to PostgreSQL via DATABASE_URL: {e}")
            sys.exit(1)

    host = os.getenv("POSTGRES_HOST", "127.0.0.1")
    port = int(os.getenv("POSTGRES_PORT", "5432"))
    dbname = os.getenv("POSTGRES_DB", "postgres")
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgres")

    print("\nConnecting to PostgreSQL (Localhost / Fallback):")
    print(f"  Host:     {host}")
    print(f"  Port:     {port}")
    print(f"  Database: {dbname}")
    print(f"  User:     {user}")

    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            dbname=dbname,
            user=user,
            password=password,
            connect_timeout=10
        )
        return conn
    except Exception as e:
        print(f"\n[ERROR] Failed to connect to PostgreSQL: {e}")
        print("\nTroubleshooting tips:")
        print("  1. Ensure PostgreSQL service is running or DATABASE_URL is configured.")
        print("  2. In PowerShell, set your password if required:")
        print("     $env:POSTGRES_PASSWORD = 'your_actual_password'")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Ingest knowledge-base chunks and embeddings into PostgreSQL.")
    parser.add_argument(
        "--truncate",
        action="store_true",
        help="Truncate the table before inserting if it already contains data."
    )
    args = parser.parse_args()

    print("=" * 80)
    print(" NXGEN TECH ACADEMY - PGVECTOR RAG DATA INGESTION PIPELINE")
    print("=" * 80)

    # Step 1: Load and Validate Source Files
    chunks, embeddings = load_and_validate_data()

    # Step 2: Connect to PostgreSQL
    conn = get_db_connection()
    conn.autocommit = False  # Enable explicit transaction control
    cur = conn.cursor()

    try:
        # Step 3: Check Table Existence & Schema
        cur.execute(f"SELECT to_regclass('public.{TABLE_NAME}');")
        table_exists = cur.fetchone()[0]
        if not table_exists:
            raise RuntimeError(
                f"Table '{TABLE_NAME}' does not exist in the database. "
                f"Please ensure the table is created before running ingestion."
            )

        # Step 4: Check Existing Row Count
        cur.execute(f"SELECT COUNT(*) FROM {TABLE_NAME};")
        existing_count = cur.fetchone()[0]
        print(f"\nCurrent rows in '{TABLE_NAME}': {existing_count}")

        if existing_count > 0:
            if not args.truncate:
                print(f"\n[!] SAFETY CHECK: Table '{TABLE_NAME}' already contains {existing_count} record(s).")
                print("    Aborting ingestion to prevent duplicate records.")
                print("    If you wish to overwrite existing records, run with the --truncate flag:")
                print("    python rag/load_embeddings.py --truncate\n")
                cur.close()
                conn.close()
                sys.exit(0)
            else:
                print(f"    --truncate flag detected: Clearing {existing_count} existing records...")
                cur.execute(f"TRUNCATE TABLE {TABLE_NAME} RESTART IDENTITY;")
                print("    Table truncated successfully.")

        # Step 5: Prepare Ingestion Data (Locked 1-to-1 Mapping)
        total_records = len(chunks)
        print(f"\nPreparing {total_records} records for insertion...")
        records = []
        for idx in range(total_records):
            chunk_item = chunks[idx]
            text = chunk_item.get("text", "")
            if not text:
                raise ValueError(f"Chunk at index #{idx} is empty or missing 'text' field.")

            vector = embeddings[idx]
            # Convert NumPy vector into pgvector string format '[v1,v2,...,v384]'
            vector_str = f"[{','.join(f'{x:.8f}' for x in vector)}]"
            records.append((text, vector_str))

        print(f"Successfully prepared {len(records)} records.")

        # Step 6: Execute Insertion Inside Transaction
        print(f"\nInserting records into '{TABLE_NAME}'...")
        insert_query = f"INSERT INTO {TABLE_NAME} (chunk_text, embedding) VALUES %s;"
        
        execute_values(
            cur,
            insert_query,
            records,
            template="(%s, %s::vector)",
            page_size=50
        )

        # Step 7: Verify Count Inside Transaction Before Commit
        cur.execute(f"SELECT COUNT(*) FROM {TABLE_NAME};")
        inserted_count = cur.fetchone()[0]

        if inserted_count != total_records:
            raise RuntimeError(
                f"Verification Error: Expected {total_records} rows in '{TABLE_NAME}', "
                f"but found {inserted_count}. Rolling back transaction."
            )

        # Commit Transaction
        conn.commit()
        print(f"Transaction successfully committed! Total rows in '{TABLE_NAME}': {inserted_count}")

        print("\n" + "=" * 80)
        print(" INGESTION SUCCESSFUL")
        print(f" Loaded {inserted_count} chunks and 384-dim embeddings into '{TABLE_NAME}'.")
        print(f" Exact 1-to-1 mapping (chunk[0..{inserted_count-1}] <-> embedding[0..{inserted_count-1}]) preserved.")
        print("=" * 80)

    except Exception as e:
        conn.rollback()
        print(f"\n[ERROR] Ingestion failed: {e}")
        print("Transaction was rolled back. No partial changes were committed to the database.")
        sys.exit(1)
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()
