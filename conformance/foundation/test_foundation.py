"""Negative contract and compatibility cases, independent of a module runtime."""
import copy
import unittest
import tempfile
from pathlib import Path
from jsonschema import ValidationError
from check import CONTRACT, compatible, load, validate


class FoundationTests(unittest.TestCase):
    def setUp(self):
        examples = CONTRACT / 'examples'
        self.module, self.instance, self.binding, self.environment = [
            load(examples / (name + '.json')) for name in
            ('module', 'instance', 'binding', 'environment-macos')]
        self.request = load(examples / 'request.json')

    def assertInvalid(self, kind, data):
        with self.assertRaises((ValidationError, ValueError)):
            validate(kind, data)

    def match(self):
        return compatible(self.module, self.instance, self.binding, self.environment)

    def test_platform_mapping_does_not_claim_runtime_support(self):
        for target in ('macos', 'windows', 'linux', 'kubernetes'):
            with self.subTest(target=target):
                self.environment = load(CONTRACT / 'examples' / f'environment-{target}.json')
                self.instance['environmentId'] = self.environment['environmentId']
                result = self.match()
                self.assertFalse(result['runtimeVerified'])
                self.assertFalse(result['accessGranted'])
                self.assertEqual(result['targetStatus'], 'untested')
                self.assertEqual(result['unresolvedRequiredDependencies'], ['farmy.authorization'])

    def test_rejects_declared_compatibility_mismatches(self):
        mutations = [
            ('instance', 'implementationVersion', '0.2.0'),
            ('instance', 'implementationId', 'another.implementation'),
            ('instance', 'environmentId', 'another.environment'),
            ('binding', 'instanceId', 'another.instance'),
            ('binding', 'capabilityId', 'farmy.something-else'),
            ('binding', 'contractVersion', '0.2-draft'),
            ('binding', 'operations', ['delete.version']),
            ('binding', 'requiredFeatures', ['streaming']),
        ]
        for name, field, value in mutations:
            with self.subTest(field=field):
                self.setUp()
                getattr(self, name)[field] = value
                with self.assertRaises(ValueError):
                    self.match()

    def test_no_credentials_in_place_of_references(self):
        self.environment['serviceCredentialRef'] = 'raw-token-value'
        self.assertInvalid('environment', self.environment)
        self.instance['apiKey'] = 'synthetic-secret'
        self.assertInvalid('instance', self.instance)

    def test_binding_cannot_embed_a_grant(self):
        self.binding['grant'] = {'allow': '*'}
        self.assertInvalid('binding', self.binding)

    def test_urls_reject_insecure_and_credential_bearing_addresses(self):
        for endpoint in ('http://localhost:8000', 'https://user:pass@example.invalid',
                         'https://example.invalid/?token=secret', 'https:///nohost',
                         'https://example.invalid/#fragment', 'https://example.invalid:0',
                         'https://example.invalid:99999', 'https://bad host.invalid',
                         'https://example.invalid\\@other.invalid'):
            with self.subTest(endpoint=endpoint):
                self.instance['endpoint'] = endpoint
                self.assertInvalid('instance', self.instance)

    def test_missing_or_unsupported_target(self):
        self.module['targets'] = [{'target': 'linux', 'status': 'untested'}]
        with self.assertRaises(ValueError):
            self.match()
        self.module['targets'] = [{'target': 'macos', 'status': 'unsupported'}]
        with self.assertRaises(ValueError):
            self.match()

    def test_duplicate_capability_rejected_even_with_different_version(self):
        another = copy.deepcopy(self.module['capabilities'][0])
        another['contractVersion'] = '0.2-draft'
        self.module['capabilities'].append(another)
        self.assertInvalid('module', self.module)

    def test_duplicate_dependency_and_target_rejected(self):
        for name, changed in [('dependencies', {'required': False}),
                              ('targets', {'status': 'experimental'})]:
            self.setUp()
            another = dict(self.module[name][0], **changed)
            self.module[name].append(another)
            self.assertInvalid('module', self.module)

    def test_unknown_profile_and_connectivity_rejected(self):
        for field, value in [('profile', 'farmy.integration/999'),
                             ('securityProfile', 'none'), ('connectivityMode', 'relay')]:
            self.setUp()
            self.instance[field] = value
            self.assertInvalid('instance', self.instance)

    def test_kubernetes_needs_provider_profile(self):
        self.environment['target'] = 'kubernetes'
        self.assertInvalid('environment', self.environment)

    def test_laptop_cannot_claim_cloud_landing_zone(self):
        self.environment['provider'] = 'scaleway'
        self.environment['landingZoneProfile'] = 'example'
        self.assertInvalid('environment', self.environment)

    def test_explicit_version_required(self):
        del self.request['inputRefs'][0]['versionId']
        self.assertInvalid('request', self.request)

    def test_cross_wallet_input_rejected_by_this_profile(self):
        self.request['inputRefs'][0]['walletId'] = 'another.wallet'
        self.assertInvalid('request', self.request)

    def test_deadline_must_be_valid_utc_time(self):
        for deadline in ('not-a-date', '2030-02-30T00:00:00Z', '2030-01-01T00:00:00'):
            self.request['deadline'] = deadline
            self.assertInvalid('request', self.request)

    def test_result_and_error_are_exclusive(self):
        response = load(CONTRACT / 'examples' / 'response.json')
        response['error'] = {'code': 'denied', 'message': 'Denied', 'retryable': False}
        self.assertInvalid('response', response)

    def test_denial_cannot_publish_output_refs(self):
        response = load(CONTRACT / 'examples' / 'response-denied.json')
        response['outputRefs'] = self.request['inputRefs']
        self.assertInvalid('response', response)

    def test_strict_json_parsing(self):
        for content in ('{"instanceId":"one","instanceId":"two"}',
                        '{"payload":{"value":NaN}}', '{"payload":{"value":Infinity}}'):
            with self.subTest(content=content), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / 'input.json'
                path.write_text(content)
                with self.assertRaises(ValueError):
                    load(path)

    def test_common_descriptor_shape_supports_all_families(self):
        for family in ('wallet', 'registry', 'workflow', 'connectors', 'processing',
                       'knowledge', 'model-access', 'assistance', 'exchange'):
            with self.subTest(family=family):
                self.module['family'] = family
                validate('module', self.module)

    def test_opaque_domain_payload_is_not_a_conformance_claim(self):
        self.request['payload'] = {'unknown-domain-data': 'not checked here'}
        validate('request', self.request)  # Full operation validation remains a runtime requirement.


if __name__ == '__main__':
    unittest.main()
