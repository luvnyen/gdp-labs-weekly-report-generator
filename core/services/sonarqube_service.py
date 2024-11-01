"""SonarQube Service Module

This module provides functionality to interact with SonarQube API for retrieving
and formatting test coverage metrics for configured components.

Authors:
    - Calvert Tanudihardjo (calvert.tanudihardjo@gdplabs.id)
"""

from collections import defaultdict
from dataclasses import dataclass
from typing import Optional, List, Dict

import requests

from config.config import SONARQUBE_USER_TOKEN, SONARQUBE_API_URL, SONARQUBE_COMPONENTS, SonarQubeComponent

TARGET_COVERAGE_PERCENTAGE = 97


@dataclass
class ComponentMetrics:
    """Container for SonarQube component metrics.

    Attributes:
        coverage (Optional[str]): Coverage percentage as string
        component_name (Optional[str]): Name of the component
        url (Optional[str]): SonarQube URL for the component
        project (Optional[str]): Project name containing the component
    """
    coverage: Optional[str] = None
    component_name: Optional[str] = None
    url: Optional[str] = None
    project: Optional[str] = None


def get_component_metrics(component: SonarQubeComponent) -> ComponentMetrics:
    """Retrieve metrics for a specific SonarQube component.

    Args:
        component (SonarQubeComponent): Component to fetch metrics for

    Returns:
        ComponentMetrics: Container with component metrics and metadata

    Note:
        Handles HTTP request errors by printing error messages and returning
        a ComponentMetrics object with partial data.
    """
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
        metrics.component_name = comp.get('name')
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
    """Get metrics for all configured SonarQube components.

    Returns:
        List[ComponentMetrics]: List of metrics for all configured components
    """
    return [get_component_metrics(component) for component in SONARQUBE_COMPONENTS]


def format_test_coverage_components(metrics_list: List[ComponentMetrics]) -> str:
    """Format test coverage metrics into a Markdown report.

    Args:
        metrics_list (List[ComponentMetrics]): List of component metrics to format

    Returns:
        str: Markdown formatted report grouped by project, with format:
            * Project1
              * Component1: [95%](url) (target: 97%)
              * Component2: [98%](url) (target: 97%)
            * Project2
              * Component3: [92%](url) (target: 97%)
    """
    if not metrics_list:
        return "* No components configured"

    projects: Dict[str, List[ComponentMetrics]] = defaultdict(list)
    for metric in metrics_list:
        if metric.project:
            projects[metric.project].append(metric)

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
    """Get test coverage for the first configured component (legacy support).

    Returns:
        Optional[str]: Coverage percentage if component exists, None otherwise
    """
    if SONARQUBE_COMPONENTS:
        metrics = get_component_metrics(SONARQUBE_COMPONENTS[0])
        return metrics.coverage
    return None
