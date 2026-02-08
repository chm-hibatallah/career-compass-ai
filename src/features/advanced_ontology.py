"""
Advanced skill ontology with hierarchies and relationships
"""
import json
from typing import Dict, List, Set, Tuple
import networkx as nx
import pandas as pd
from collections import defaultdict
import yaml
from pathlib import Path

class AdvancedSkillOntology:
    """Advanced skill ontology with hierarchies, prerequisites, and relationships"""
    
    def __init__(self, ontology_file: str = None):
        self.skill_graph = nx.DiGraph()
        self.skill_categories = {}
        self.skill_levels = {}
        self.skill_relationships = {}
        
        # Load or create default ontology
        if ontology_file and Path(ontology_file).exists():
            self.load_ontology(ontology_file)
        else:
            self.build_default_ontology()
    
    def build_default_ontology(self):
        """Build a comprehensive skill ontology"""
        
        # Skill categories hierarchy
        self.skill_categories = {
            'programming': {
                'description': 'Programming languages and frameworks',
                'skills': ['python', 'r', 'java', 'javascript', 'sql', 'scala', 'go', 'rust'],
                'subcategories': {
                    'python_ecosystem': ['python', 'django', 'flask', 'fastapi', 'numpy', 'pandas'],
                    'web_dev': ['javascript', 'react', 'vue', 'node.js', 'typescript'],
                    'jvm_languages': ['java', 'scala', 'kotlin']
                }
            },
            'data_science': {
                'description': 'Data science and machine learning',
                'skills': ['machine learning', 'statistics', 'data visualization', 'deep learning', 'nlp'],
                'subcategories': {
                    'ml_frameworks': ['tensorflow', 'pytorch', 'scikit-learn', 'keras', 'mxnet'],
                    'data_viz': ['matplotlib', 'seaborn', 'plotly', 'tableau', 'powerbi'],
                    'big_data': ['spark', 'hadoop', 'hive', 'presto', 'kafka']
                }
            },
            'cloud_devops': {
                'description': 'Cloud computing and DevOps',
                'skills': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'ci_cd'],
                'subcategories': {
                    'cloud_platforms': ['aws', 'azure', 'gcp', 'ibm cloud', 'oracle cloud'],
                    'containerization': ['docker', 'kubernetes', 'openshift', 'rancher'],
                    'infrastructure': ['terraform', 'ansible', 'puppet', 'chef']
                }
            },
            'data_engineering': {
                'description': 'Data engineering and pipelines',
                'skills': ['etl', 'data pipelines', 'airflow', 'dbt', 'data warehousing'],
                'subcategories': {
                    'orchestration': ['airflow', 'luigi', 'prefect', 'dagster'],
                    'databases': ['postgresql', 'mysql', 'mongodb', 'cassandra', 'redis'],
                    'streaming': ['kafka', 'flink', 'spark streaming', 'pulsar']
                }
            },
            'soft_skills': {
                'description': 'Professional and interpersonal skills',
                'skills': ['communication', 'leadership', 'problem solving', 'teamwork', 'project management'],
                'subcategories': {
                    'communication': ['technical writing', 'presentation', 'stakeholder management'],
                    'leadership': ['mentoring', 'team leadership', 'strategic thinking']
                }
            }
        }
        
        # Skill relationships (prerequisites, co-requisites, next-steps)
        self.skill_relationships = {
            'python': {
                'prerequisites': ['programming fundamentals'],
                'co_requisites': ['sql'],
                'next_steps': ['pandas', 'numpy', 'machine learning'],
                'difficulty': 'beginner',
                'estimated_hours': 40
            },
            'machine learning': {
                'prerequisites': ['python', 'statistics', 'linear algebra'],
                'co_requisites': ['numpy', 'pandas'],
                'next_steps': ['deep learning', 'mlops', 'nlp'],
                'difficulty': 'intermediate',
                'estimated_hours': 60
            },
            'aws': {
                'prerequisites': ['cloud fundamentals'],
                'co_requisites': ['linux', 'networking basics'],
                'next_steps': ['docker', 'kubernetes', 'terraform'],
                'difficulty': 'intermediate',
                'estimated_hours': 50
            },
            'docker': {
                'prerequisites': ['linux basics'],
                'co_requisites': ['python', 'devops concepts'],
                'next_steps': ['kubernetes', 'ci_cd'],
                'difficulty': 'beginner',
                'estimated_hours': 25
            }
        }
        
        # Build the graph
        self._build_skill_graph()
    
    def _build_skill_graph(self):
        """Build network graph of skill relationships"""
        
        # Add nodes with attributes
        for category, data in self.skill_categories.items():
            for skill in data['skills']:
                self.skill_graph.add_node(skill.lower(), category=category, type='primary')
            
            for subcat, subskills in data.get('subcategories', {}).items():
                for skill in subskills:
                    self.skill_graph.add_node(skill.lower(), category=category, subcategory=subcat, type='specific')
        
        # Add relationships
        for skill, relations in self.skill_relationships.items():
            skill_lower = skill.lower()
            
            # Add prerequisite edges
            for prereq in relations.get('prerequisites', []):
                self.skill_graph.add_edge(prereq.lower(), skill_lower, relationship='prerequisite', weight=0.8)
            
            # Add co-requisite edges
            for coreq in relations.get('co_requisites', []):
                self.skill_graph.add_edge(coreq.lower(), skill_lower, relationship='co_requisite', weight=0.5)
                self.skill_graph.add_edge(skill_lower, coreq.lower(), relationship='co_requisite', weight=0.5)
            
            # Add next-step edges
            for next_skill in relations.get('next_steps', []):
                self.skill_graph.add_edge(skill_lower, next_skill.lower(), relationship='progression', weight=0.7)
    
    def find_learning_path(self, current_skills: List[str], target_skill: str) -> Dict:
        """Find optimal learning path to target skill"""
        current_skills_lower = [s.lower() for s in current_skills]
        target_skill_lower = target_skill.lower()
        
        if target_skill_lower not in self.skill_graph:
            return {'error': f'Skill "{target_skill}" not in ontology'}
        
        # Find shortest path from current skills to target
        paths = []
        for start_skill in current_skills_lower:
            if start_skill in self.skill_graph:
                try:
                    path = nx.shortest_path(self.skill_graph, start_skill, target_skill_lower)
                    paths.append(path)
                except nx.NetworkXNoPath:
                    continue
        
        if not paths:
            return {'error': 'No learning path found'}
        
        # Choose shortest path
        shortest_path = min(paths, key=len)
        
        # Calculate path metrics
        total_hours = 0
        path_details = []
        
        for i, skill in enumerate(shortest_path):
            skill_data = {
                'skill': skill,
                'step': i + 1,
                'category': self.skill_graph.nodes[skill].get('category', 'unknown'),
                'relationships': []
            }
            
            # Get relationships with previous and next skills
            if i > 0:
                prev_skill = shortest_path[i-1]
                edge_data = self.skill_graph.get_edge_data(prev_skill, skill)
                if edge_data:
                    skill_data['relationships'].append({
                        'from': prev_skill,
                        'relationship': edge_data.get('relationship', 'unknown'),
                        'reason': self._get_relationship_reason(prev_skill, skill)
                    })
            
            # Estimate hours
            if skill in self.skill_relationships:
                skill_data['estimated_hours'] = self.skill_relationships[skill].get('estimated_hours', 30)
                skill_data['difficulty'] = self.skill_relationships[skill].get('difficulty', 'intermediate')
                total_hours += skill_data['estimated_hours']
            else:
                skill_data['estimated_hours'] = 30
                skill_data['difficulty'] = 'intermediate'
                total_hours += 30
            
            path_details.append(skill_data)
        
        return {
            'path': shortest_path,
            'details': path_details,
            'total_steps': len(shortest_path),
            'total_hours': total_hours,
            'new_skills_count': len([s for s in shortest_path if s not in current_skills_lower])
        }
    
    def _get_relationship_reason(self, skill_a: str, skill_b: str) -> str:
        """Get human-readable reason for relationship"""
        relationships = {
            'prerequisite': f"Knowing {skill_a} is essential for understanding {skill_b}",
            'co_requisite': f"{skill_a} and {skill_b} are often used together",
            'progression': f"{skill_a} naturally leads to learning {skill_b}"
        }
        
        edge_data = self.skill_graph.get_edge_data(skill_a, skill_b)
        if edge_data:
            rel_type = edge_data.get('relationship', 'unknown')
            return relationships.get(rel_type, f"Related to {skill_b}")
        
        return "Related concept"
    
    def get_skill_cluster(self, skill: str, depth: int = 2) -> Dict:
        """Get cluster of related skills"""
        skill_lower = skill.lower()
        
        if skill_lower not in self.skill_graph:
            return {'error': f'Skill "{skill}" not in ontology'}
        
        # Get neighbors within specified depth
        ego_graph = nx.ego_graph(self.skill_graph, skill_lower, radius=depth)
        
        cluster = {
            'central_skill': skill_lower,
            'related_skills': [],
            'prerequisites': [],
            'next_steps': []
        }
        
        for node in ego_graph.nodes():
            if node != skill_lower:
                edge_data = self.skill_graph.get_edge_data(skill_lower, node)
                if edge_data:
                    rel_type = edge_data.get('relationship', 'unknown')
                    
                    skill_info = {
                        'skill': node,
                        'relationship': rel_type,
                        'category': self.skill_graph.nodes[node].get('category', 'unknown')
                    }
                    
                    if rel_type == 'prerequisite':
                        cluster['prerequisites'].append(skill_info)
                    elif rel_type == 'progression':
                        cluster['next_steps'].append(skill_info)
                    else:
                        cluster['related_skills'].append(skill_info)
        
        return cluster
    
    def save_ontology(self, filepath: str):
        """Save ontology to file"""
        ontology_data = {
            'skill_categories': self.skill_categories,
            'skill_relationships': self.skill_relationships,
            'graph_data': nx.node_link_data(self.skill_graph)
        }
        
        with open(filepath, 'w') as f:
            yaml.dump(ontology_data, f, default_flow_style=False)
        
        print(f"✅ Ontology saved to {filepath}")
    
    def load_ontology(self, filepath: str):
        """Load ontology from file"""
        with open(filepath, 'r') as f:
            ontology_data = yaml.safe_load(f)
        
        self.skill_categories = ontology_data.get('skill_categories', {})
        self.skill_relationships = ontology_data.get('skill_relationships', {})
        
        # Reconstruct graph
        self.skill_graph = nx.node_link_graph(ontology_data.get('graph_data', {}))
        
        print(f"✅ Ontology loaded from {filepath}")