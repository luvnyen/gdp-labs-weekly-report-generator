"""SonarQube Service Module

This module provides functionality to interact with SonarQube API for retrieving
and formatting test coverage metrics for configured components.

Authors:
    - Calvert Tanudihardjo (calvert.tanudihardjo@gdplabs.id)
"""

from dataclasses import dataclass
from typing import Optional, List, Dict
from collections import defaultdict
import requests
from config.config import SONARQUBE_USER_TOKEN, SONARQUBE_API_URL, SONARQUBE_COMPONENTS, SonarQubeComponent

TARGET_COVERAGE_PERCENTAGE = 97

@dataclass
class ComponentMetrics:
    coverage: Optional[str] = None
    component_name: Optional[str] = None
    url: Optional[str] = None
    project: Optional[str] = None

def get_component_metrics(component: SonarQubeComponent) -> ComponentMetrics:
    params = {
        'component': component.full_key,
        'metricKeys': 'coverage'
    }

    headers = {
        'accept': 'application/json',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
    }

    auth = (SONARQUBE_USER_TOKEN, '')

    metrics = ComponentMetrics()
    metrics.url = component.url
    metrics.project = component.project

    response = requests.get(SONARQUBE_API_URL, params=params, headers=headers, auth=auth)

    if response.status_code == 200:
        json_response = response.json()
        comp = json_response.get('component', {})
        
        # Get component name
        metrics.component_name = comp.get('name')
        
        # Get coverage
        measures = comp.get('measures', [])
        metrics.coverage = next(
            (measure['value'] for measure in measures if measure['metric'] == 'coverage'),
            None
        )
    else:
        print(f"Request failed for component {component.full_key} with status code: {response.status_code}")
        print(response.text)
    
    return metrics

def get_all_components_metrics() -> List[ComponentMetrics]:
    """Get metrics for all configured SonarQube components."""
    return [get_component_metrics(component) for component in SONARQUBE_COMPONENTS]

def format_test_coverage_components(metrics_list: List[ComponentMetrics]) -> str:
    """Format the test coverage components for the report, grouped by project."""
    if not metrics_list:
        return "* No components configured"
    
    # Group metrics by project
    projects: Dict[str, List[ComponentMetrics]] = defaultdict(list)
    for metric in metrics_list:
        if metric.project:
            projects[metric.project].append(metric)
    
    # Format output with grouping
    output_lines = []
    for project in sorted(projects.keys()):
        output_lines.append(f"* {project}")
        for metric in sorted(projects[project], key=lambda m: m.component_name or ''):
            output_lines.append(
                f"  * {metric.component_name or 'unknown'}: "
                f"[{metric.coverage or 'N/A'}%]({metric.url}) (target: {TARGET_COVERAGE_PERCENTAGE}%)"
            )
    
    return '\n'.join(output_lines)

def get_test_coverage() -> Optional[str]:
    """For backward compatibility."""
    if SONARQUBE_COMPONENTS:
        metrics = get_component_metrics(SONARQUBE_COMPONENTS[0])
        return metrics.coverage
    return None