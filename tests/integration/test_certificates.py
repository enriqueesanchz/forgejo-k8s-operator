#!/usr/bin/env python3

"""Integration test covering the certificates endpoint (requires, tls-certificates)."""

import logging

import jubilant

logger = logging.getLogger(__name__)


def test_certificates_relation(deployed_app, juju: jubilant.Juju):
    """Verify Forgejo switches to HTTPS and stays active when related to a TLS provider."""
    juju.deploy("self-signed-certificates", "self-signed-certificates", channel="latest/stable")
    juju.integrate(f"{deployed_app}:certificates", "self-signed-certificates:certificates")

    juju.wait(
        lambda status: jubilant.all_active(status, deployed_app, "self-signed-certificates"),
        timeout=600,
    )

    juju.remove_relation(f"{deployed_app}:certificates", "self-signed-certificates:certificates")
    juju.remove_application("self-signed-certificates")

    # Forgejo should revert cleanly to HTTP once certificates are removed.
    juju.wait(lambda status: jubilant.all_active(status, deployed_app), timeout=300)
