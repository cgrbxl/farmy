# UC-007 — S3 source, in progress

**Status: local implementation verified; real Scaleway validation pending.** Eleven local checks and an end-to-end HTTP-double demonstration pass. Six earlier slices remain the delivered baseline. No cloud resource has been accessed or provisioned for this increment.

The S3 implementation takes the existing Connector role in a fresh seven-process composition: Wallet, S3 Connector, Processing, Knowledge, Workflow, Exchange and the synthetic recipient. Six Farmy services can be monitored through the existing read-only dashboard. The S3 provider is a separate dependency, outside the Farmy mTLS boundary.

## Run now without a cloud account

From the repository root:

```sh
.venv/bin/python -m pip install -r modules/connectors/s3/requirements.txt
.venv/bin/python solutions/s3-source/uc007/run.py demo --fixture
.venv/bin/python solutions/s3-source/uc007/run.py launch --fixture
```

`demo` prints checks and stops all owned processes. `launch` keeps the local HTTP double and Farmy composition running and prints a monitoring access link. Open that link; select **S3 Source** or **Controlled Exchange**. Ctrl-C stops the runner and its processes. Port selection follows UC-006: prefer 8766, automatically choose a free port if occupied, or use `--port 0`.

This fixture mode is explicitly labelled, uses fixed synthetic credentials and permits only loopback HTTP. It cannot accept real credential references. It establishes local behaviour, not Scaleway support. Snapshot state is temporary and removed after exit. Local stores and development keys are unencrypted; use synthetic documents only.

## Finish the real-provider validation

Required input: an approved **existing Scaleway bucket**, **region**, **dedicated test prefix**, and an explicitly selected **scoped credential reference**. Do not paste keys in chat or commit them. A provider selection alone does not authorise cloud provisioning or IAM changes.

1. Supply a non-secret settings file based on [the example](../../../modules/connectors/s3/scaleway.example.json), kept under ignored `.farmy/`. Choose the exact regional endpoint and a named static credential profile or environment references. See [credential and permission boundaries](../../../modules/connectors/s3/README.md).
2. Place the included [synthetic report](report.txt) at `<approved-prefix>/report.txt` through an authorised provider workflow. The connector and demo are read-only against S3 and never create/overwrite/delete objects or change versioning. Any automated fixture-writing plan must be separately bounded to the agreed prefix and authorised before execution.
3. Run the same pipeline with explicit provider settings:

```sh
.venv/bin/python solutions/s3-source/uc007/run.py demo --s3-config .farmy/uc007-scaleway.json --key report.txt
```

The run captures the object, extracts `crop: wheat`, retrieves exact-source evidence and delivers the approved original bytes to a local synthetic recipient. It checks restart and export revocation. It performs provider reads, which may incur the provider's normal request/transfer charges; it creates no bucket or other cloud infrastructure.

4. Retain sanitised evidence for actual provider version/conditional-read behaviour and a provider-denied read using a known test restriction. If overwrite/versioning tests require provider mutations, agree the exact synthetic keys and bounded changes first. Do not infer live conditional-write-race or IAM results from the local double.
5. Record exact revision, region, SDK/runtime versions and results without publishing bucket names, keys or credentials. Only then update the slice to done and the dashboard to seven delivered slices.

## Independent operation

`bootstrap --directory .farmy/uc007 --s3-config .farmy/uc007-scaleway.json` creates a fresh local composition without reading S3. Start each identity with `serve --directory .farmy/uc007 --service ID`: `wallet.local`, `connector.local`, `processing.local`, `knowledge.local`, `workflow.local`, `exchange.local`, `recipient.local`. Then `exercise --directory .farmy/uc007 --key report.txt` performs the pipeline, and `dashboard --directory .farmy/uc007` monitors it. Independent services stay running when that separate bridge stops.

Bootstrap needs an empty directory. Development certificates last two days; no rotation or migration tool is supplied. Environment credential references must be available to the Connector process. Credentials resolve at startup; restart after changing them. Do not point this composition at an existing Local Folder state directory.

## Verification

```sh
.venv/bin/python -m unittest discover -s conformance/uc007 -v
.venv/bin/python scripts/verify.py --with-local-model --with-s3-fixture
```

The optional S3 flag adds 11 checks and one local-double demonstration to the previous 80 tests and six demos. It does not run against a provider. The default verification command remains usable without the optional S3 dependencies.

See the [use-case card](../use-cases/UC-007-s3-source.md). Unsupported today: simultaneous Local Folder/S3 sources in one Wallet, generic endpoint providers, multipart/large objects, streaming acquisition, provider-native provenance API, production key custody, Windows/Linux/Kubernetes packaging and the Scaleway landing zone.

## Recorded local verification

On 2026-09-21, macOS 26.6.2 arm64 / Python 3.14.6: the combined runner with `--with-local-model --with-s3-fixture` passed all 91 checks and seven demos, including the installed local Qwen run. Browser inspection confirmed six monitored Farmy instances and the S3 Source (fixture) snapshot counts. Real Scaleway validation was not performed; no cloud resources were accessed or changed.

Local implementation evidence: [`e82e0cf`](https://github.com/cgrbxl/farmy/commit/e82e0cf). This revision records local checks only; provider verification remains pending.
