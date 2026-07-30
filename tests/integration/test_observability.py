#!/usr/bin/env python3

"""Integration tests covering the observability-related endpoints.

These cover the endpoints not exercised elsewhere: logging (requires,
loki_push_api), metrics-endpoint (provides, prometheus_scrape) and
grafana-dashboard (provides, grafana_dashboard).
"""

import logging

import jubilant

logger = logging.getLogger(__name__)


def test_logging_relation(deployed_app, juju: jubilant.Juju):
    """Verify Forgejo stays active when related to loki-k8s over the logging endpoint."""
    juju.deploy("loki-k8s", "loki-k8s", channel="1/stable", trust=True)
    juju.integrate(f"{deployed_app}:logging", "loki-k8s:logging")

    status = juju.wait(
        lambda status: jubilant.all_active(status, deployed_app, "loki-k8s"),
        timeout=600,
    )
    assert jubilant.all_active(status, deployed_app, "loki-k8s")

    juju.remove_relation(f"{deployed_app}:logging", "loki-k8s:logging")
    juju.remove_application("loki-k8s")

    status = juju.wait(lambda status: jubilant.all_active(status, deployed_app), timeout=300)
    assert jubilant.all_active(status, deployed_app)


def test_metrics_endpoint_relation(deployed_app, juju: jubilant.Juju):
    """Verify Forgejo stays active when related to prometheus-k8s over metrics-endpoint."""
    juju.deploy("prometheus-k8s", "prometheus-k8s", channel="2/stable", trust=True)
    juju.integrate(f"{deployed_app}:metrics-endpoint", "prometheus-k8s:metrics-endpoint")

    status = juju.wait(
        lambda status: jubilant.all_active(status, deployed_app, "prometheus-k8s"),
        timeout=600,
    )
    assert jubilant.all_active(status, deployed_app, "prometheus-k8s")

    juju.remove_relation(f"{deployed_app}:metrics-endpoint", "prometheus-k8s:metrics-endpoint")
    juju.remove_application("prometheus-k8s")

    status = juju.wait(lambda status: jubilant.all_active(status, deployed_app), timeout=300)
    assert jubilant.all_active(status, deployed_app)


def test_grafana_dashboard_relation(deployed_app, juju: jubilant.Juju):
    """Verify Forgejo stays active when related to grafana-k8s over grafana-dashboard."""
    juju.deploy("grafana-k8s", "grafana-k8s", channel="2/stable", trust=True)
    juju.integrate(f"{deployed_app}:grafana-dashboard", "grafana-k8s:grafana-dashboard")

    status = juju.wait(
        lambda status: jubilant.all_active(status, deployed_app, "grafana-k8s"),
        timeout=600,
    )
    assert jubilant.all_active(status, deployed_app, "grafana-k8s")

    juju.remove_relation(f"{deployed_app}:grafana-dashboard", "grafana-k8s:grafana-dashboard")
    juju.remove_application("grafana-k8s")

    status = juju.wait(lambda status: jubilant.all_active(status, deployed_app), timeout=300)
    assert jubilant.all_active(status, deployed_app)
