# scripts/load_esco_to_neo4j.py

import pandas as pd
from py2neo import Graph, Node, Relationship
from dotenv import load_dotenv
import os

load_dotenv()

# ─────────────────────────────────────────────────────────────
# STEP 1 — Connect to Neo4j
# ─────────────────────────────────────────────────────────────
print("Step 1 — Connecting to Neo4j...")

graph = Graph(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))
)
print("  Connected")

# ─────────────────────────────────────────────────────────────
# STEP 2 — Load skills CSV
# We keep all skill types — both skill/competence and knowledge
# are relevant for resume matching
# ─────────────────────────────────────────────────────────────
print("\nStep 2 — Loading skills CSV...")

skills_df = pd.read_csv("ESCO dataset - v1.2.1 - classification - en - csv/skills_en.csv")
print(f"  Loaded {len(skills_df)} skills")

# ─────────────────────────────────────────────────────────────
# STEP 3 — Create skill nodes in Neo4j
# Each skill becomes a node with:
#   - uri: unique identifier used to link with relations
#   - name: canonical preferred label lowercased
#   - alt_labels: pipe separated alternative names
#   - skill_type: skill/competence or knowledge
# We use merge not create to avoid duplicates on reruns
# ─────────────────────────────────────────────────────────────
print("\nStep 3 — Creating skill nodes...")

# Create uniqueness constraint first so merges are fast
graph.run("CREATE CONSTRAINT skill_uri IF NOT EXISTS FOR (s:Skill) REQUIRE s.uri IS UNIQUE")

for i, row in skills_df.iterrows():
    # Parse alt labels — separated by \n in ESCO
    alt_labels = ""
    if pd.notna(row["altLabels"]):
        alts = [a.strip().lower() for a in str(row["altLabels"]).split("\n") if a.strip()]
        alt_labels = "|".join(alts)

    node = Node(
        "Skill",
        uri=row["conceptUri"],
        name=str(row["preferredLabel"]).lower().strip(),
        alt_labels=alt_labels,
        skill_type=str(row["skillType"]).strip()
    )
    graph.merge(node, "Skill", "uri")

    if i % 1000 == 0:
        print(f"  {i}/{len(skills_df)} nodes created")

print(f"  Done — {len(skills_df)} skill nodes created")

# ─────────────────────────────────────────────────────────────
# STEP 4 — Load relations CSV
# Each row is a directional relationship between two skills
# relationType is either "essential" or "optional"
# essential — strong dependency, high match confidence (0.9)
# optional  — loosely related, lower match confidence (0.7)
# ─────────────────────────────────────────────────────────────
print("\nStep 4 — Loading relations CSV...")

relations_df = pd.read_csv("ESCO dataset - v1.2.1 - classification - en - csv/skillSkillRelations_en.csv")
print(f"  Loaded {len(relations_df)} relations")
print(f"  Relation types:\n{relations_df['relationType'].value_counts()}")

# ─────────────────────────────────────────────────────────────
# STEP 5 — Create relationships in Neo4j
# We look up both nodes by uri and create the relationship
# Skipping any relations where one or both nodes are missing
# ─────────────────────────────────────────────────────────────
print("\nStep 5 — Creating relationships...")

skipped = 0
created = 0

for i, row in relations_df.iterrows():
    skill_a = graph.nodes.match("Skill", uri=row["originalSkillUri"]).first()
    skill_b = graph.nodes.match("Skill", uri=row["relatedSkillUri"]).first()

    if not skill_a or not skill_b:
        skipped += 1
        continue

    rel_type = row["relationType"].upper()  # ESSENTIAL or OPTIONAL
    rel = Relationship(skill_a, rel_type, skill_b)
    graph.merge(rel)
    created += 1

    if i % 1000 == 0:
        print(f"  {i}/{len(relations_df)} relations processed")

print(f"  Done — {created} relationships created, {skipped} skipped")

# ─────────────────────────────────────────────────────────────
# STEP 6 — Verify the graph
# Quick sanity check to make sure everything loaded correctly
# ─────────────────────────────────────────────────────────────
print("\nStep 6 — Verifying graph...")

node_count = graph.run("MATCH (s:Skill) RETURN count(s) as count").data()[0]["count"]
rel_count  = graph.run("MATCH ()-[r:ESSENTIAL|OPTIONAL]->() RETURN count(r) as count").data()[0]["count"]

print(f"  Total skill nodes:    {node_count}")
print(f"  Total relationships:  {rel_count}")

# Sample query — find skills related to Python
sample = graph.run("""
    MATCH (s:Skill {name: 'python'})-[r:ESSENTIAL|OPTIONAL]-(related:Skill)
    RETURN related.name as name, type(r) as relation_type
    LIMIT 5
""").data()

print(f"\n  Sample — skills related to 'python':")
for row in sample:
    print(f"    [{row['relation_type']}] {row['name']}")

print("\nDone! ESCO graph loaded successfully")