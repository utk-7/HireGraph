import csv
import json
import os

from data_gen import DataGenerator
from data_patterns import PatternInjector


def export_to_csv(nodes_dict, relationships_list, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    # Export Nodes
    for node_label, nodes in nodes_dict.items():
        if not nodes:
            continue

        file_path = os.path.join(output_dir, f"nodes_{node_label}.csv")
        # Extract all possible keys across all nodes of this type
        keys = set()
        for n in nodes:
            keys.update(n.keys())
        keys = sorted(list(keys))

        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(nodes)

    # Export Relationships by type
    rel_types = {}
    for r in relationships_list:
        rel_type = r["rel_type"]
        if rel_type not in rel_types:
            rel_types[rel_type] = []
        rel_types[rel_type].append(r)

    for rel_type, rels in rel_types.items():
        if not rels:
            continue

        file_path = os.path.join(output_dir, f"rels_{rel_type}.csv")
        keys = set()
        for r in rels:
            keys.update(r.keys())
        keys = sorted(list(keys))

        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(rels)


def run_generation(seed, scale, output_dir):
    print(f"Generating data with seed {seed}, scale {scale}...")
    gen = DataGenerator(seed=seed, scale_factor=scale)
    nodes, rels = gen.generate_all()

    injector = PatternInjector(nodes, rels, seed=seed)
    nodes, rels = injector.run_all()

    export_to_csv(nodes, rels, output_dir)
    print(f"Exported to {output_dir}")

    # Print stats
    total_nodes = sum(len(n) for n in nodes.values())
    print(f"Total Nodes: {total_nodes}")
    total_rels = len(rels)
    print(f"Total Relationships: {total_rels}")

    interview_reviews = sum(
        1
        for n in nodes.get("Review", [])
        if n.get("review_type") == "interview_experience"
    )
    employee_reviews = sum(
        1
        for n in nodes.get("Review", [])
        if n.get("review_type") == "employee_experience"
    )
    print(f"Interview Reviews: {interview_reviews}")
    print(f"Employee Reviews: {employee_reviews}")
    print(f"Total Candidates: {len(nodes.get('Candidate', []))}")

    # Write patterns json for reference
    with open(os.path.join(output_dir, "pattern_targets.json"), "w") as f:
        json.dump(injector.target_ids, f, indent=2)


if __name__ == "__main__":
    import sys

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))

    # Test reproducibility
    # sample1_dir = os.path.join(base_dir, "sample_1")
    # sample2_dir = os.path.join(base_dir, "sample_2")

    # run_generation(seed=42, scale=1, output_dir=sample1_dir)
    # run_generation(seed=42, scale=1, output_dir=sample2_dir)

    # Run full generation
    generated_dir = os.path.join(base_dir, "generated")
    run_generation(seed=999, scale=10, output_dir=generated_dir)

    # We will let the bash script or next step move sample_1 to sample
    print("Done.")
