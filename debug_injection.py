import json
import os
import sys
sys.path.append('data_generation')
from data_generation.data_gen import DataGenerator
from data_generation.data_patterns import PatternInjector

generator = DataGenerator(seed=999, scale_factor=10)
nodes, rels = generator.generate_all()
injector = PatternInjector(nodes, rels, seed=999)

target_dept = nodes['Department'][0]
dept_jobs = [r['target_id'] for r in rels if r['source_id'] == target_dept['id'] and r['rel_type'] == 'POSTED']

offer_count = 0
for app in nodes['Application']:
    job_rel = next((r for r in rels if r['source_id'] == app['id'] and r['rel_type'] == 'FOR_POSTING'), None)
    offer_rel = next((r for r in rels if r['source_id'] == app['id'] and r['rel_type'] == 'RESULTED_IN'), None)
    if job_rel and job_rel['target_id'] in dept_jobs and offer_rel:
        offer_count += 1

print(f'Target dept: {target_dept}')
print(f'Jobs: {len(dept_jobs)}')
print(f'Offers injected: {offer_count}')
