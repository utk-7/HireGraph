import csv
import os
import sys

from dotenv import load_dotenv
from neo4j import GraphDatabase

# Load .env
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")


def run_constraints(driver):
    with open(
        os.path.join(os.path.dirname(__file__), "01_constraints.cypher"), "r"
    ) as f:
        content = f.read()

    statements = [s.strip() for s in content.split(";") if s.strip()]
    with driver.session() as session:
        for stmt in statements:
            session.run(stmt)
            print(f"Executed: {stmt[:50]}...")


def batch_iterable(iterable, batch_size):
    batch = []
    for item in iterable:
        batch.append(item)
        if len(batch) >= batch_size:
            yield batch
            batch = []
    if batch:
        yield batch


def load_data(driver, data_dir):
    files = sorted(os.listdir(os.path.dirname(__file__)))
    migration_files = [
        f for f in files if f.endswith(".cypher") and f != "01_constraints.cypher"
    ]

    for script_file in migration_files:
        # e.g., 02_load_nodes_Company.cypher -> nodes_Company.csv
        parts = script_file.replace(".cypher", "").split("_load_")
        if len(parts) < 2:
            continue

        csv_filename = parts[1] + ".csv"
        csv_path = os.path.join(data_dir, csv_filename)
        script_path = os.path.join(os.path.dirname(__file__), script_file)

        if not os.path.exists(csv_path):
            print(f"WARNING: CSV {csv_path} not found. Skipping {script_file}.")
            continue

        with open(script_path, "r") as f:
            cypher_query = f.read()

        print(f"\n--- Running {script_file} against {csv_filename} ---")

        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            total_loaded = 0

            with driver.session() as session:
                for batch in batch_iterable(reader, 1000):
                    session.execute_write(
                        lambda tx, q, p: tx.run(q, rows=p), cypher_query, batch
                    )
                    total_loaded += len(batch)
                    print(f"  Loaded {total_loaded} rows...")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_migrations.py <path_to_data_dir>")
        sys.exit(1)

    data_dir = sys.argv[1]
    print(f"Connecting to AuraDB at {NEO4J_URI}...")

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    try:
        print("Ensuring constraints...")
        run_constraints(driver)

        print(f"Starting batched load from {data_dir}...")
        load_data(driver, data_dir)
        print("\nAll migrations completed successfully!")
    finally:
        driver.close()
