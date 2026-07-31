#!/usr/bin/env python3

"""Integration test covering the s3-credentials endpoint (requires, s3)."""

import logging

import jubilant

logger = logging.getLogger(__name__)


def test_s3_credentials_relation(deployed_app, juju: jubilant.Juju):
    """Verify Forgejo stays active when related to s3-integrator over s3-credentials."""
    juju.deploy("s3-integrator", "s3-integrator", channel="latest/stable")
    juju.config(
        "s3-integrator",
        {
            "endpoint": "https://s3.example.com",
            "bucket": "forgejo-test-bucket",
            "region": "us-east-1",
        },
    )

    # Wait for a leader to be elected before running a leader-only action.
    juju.wait(
        lambda status: jubilant.all_agents_idle(status, "s3-integrator"),
        timeout=600,
    )
    juju.run(
        "s3-integrator/leader",
        "sync-s3-credentials",
        params={"access-key": "test-access-key", "secret-key": "test-secret-key"},
    )
    juju.integrate(f"{deployed_app}:s3-credentials", "s3-integrator:s3-credentials")

    # s3-integrator itself may go blocked/idle without a reachable bucket; what
    # matters here is that Forgejo consumes the relation data without erroring.
    status = juju.wait(
        lambda status: jubilant.all_active(status, deployed_app),
        timeout=600,
    )
    assert jubilant.all_active(status, deployed_app)

    juju.remove_relation(f"{deployed_app}:s3-credentials", "s3-integrator:s3-credentials")
    juju.remove_application("s3-integrator")

    status = juju.wait(lambda status: jubilant.all_active(status, deployed_app), timeout=300)
    assert jubilant.all_active(status, deployed_app)
