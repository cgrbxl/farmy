# Scaleway provider adapter

Status: first provider selected; no infrastructure implementation or validated landing zone exists.

The canonical design is the [Scaleway landing-zone plan](../../../docs/providers/scaleway.md), governed by the [common cloud requirements](../../../docs/cloud-landing-zones.md). This directory is the future home of the provider implementation and its verification, not a second copy of the design.

A deployable adapter must map account/project, network, IAM, keys/secrets, Kubernetes, storage, telemetry, recovery and cost controls to exact supported services/settings. It provides a versioned non-secret environment descriptor consumed by [Kubernetes workload packages](../../profiles/kubernetes/README.md).

Module architecture and implementation come first. Project/region, budget, tooling and provisioning remain deferred. No real infrastructure state, credentials or account identifiers belong in public examples. Provisioning requires an authorised concrete plan.
