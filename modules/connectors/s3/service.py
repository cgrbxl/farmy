"""Read-only bounded Scaleway S3 acquisition behind the existing storage contract."""
import argparse
import configparser
import json
import os
from pathlib import Path
import re
from urllib.parse import urlsplit

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError

from farmy_transport.http import Fault, MAX_BYTES, serve
from farmy_transport.snapshots import SnapshotConnector

REGIONS = ('fr-par', 'nl-ams', 'pl-waw', 'it-mil')
FIXTURE_ACCESS = 'farmy-fixture'
FIXTURE_SECRET = 'synthetic-fixture-not-a-secret'


def relative_key(value):
    if (not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._/-]{0,511}', value)
            or any(part in ('', '.', '..') for part in value.split('/'))):
        raise Fault('denied')
    return value


def validate_settings(settings):
    allowed = {'region', 'endpoint', 'bucket', 'prefix', 'credentialProfile', 'accessKeyEnv',
               'secretKeyEnv', 'sessionTokenEnv', 'fixture'}
    if not isinstance(settings, dict) or set(settings) - allowed:
        raise ValueError('Unsupported S3 configuration field')
    for field in ('region', 'endpoint', 'bucket', 'prefix'):
        if not isinstance(settings.get(field), str):
            raise ValueError('Required S3 configuration field is missing')
    for field in ('accessKeyEnv', 'secretKeyEnv', 'sessionTokenEnv'):
        if field in settings and (not isinstance(settings[field], str) or not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', settings[field])):
            raise ValueError('Use an environment variable name, not a secret value')
    if 'credentialProfile' in settings and (not isinstance(settings['credentialProfile'], str) or not settings['credentialProfile']):
        raise ValueError('A named static credential profile is required')
    if 'fixture' in settings and not isinstance(settings['fixture'], bool):
        raise ValueError('Fixture mode must be an explicit boolean')
    if settings['region'] not in REGIONS:
        raise ValueError('Unsupported Scaleway region')
    if not re.fullmatch(r'[a-z0-9][a-z0-9.-]{1,61}[a-z0-9]', settings.get('bucket', '')):
        raise ValueError('A bucket name is required')
    prefix = settings.get('prefix', '')
    if not prefix.endswith('/') or len(prefix) > 128:
        raise ValueError('A dedicated nonempty prefix ending in / is required')
    relative_key(prefix[:-1])
    parsed = urlsplit(settings.get('endpoint', ''))
    if settings.get('fixture') is True:
        if (parsed.scheme != 'http' or parsed.hostname != '127.0.0.1' or not parsed.port
                or parsed.path or parsed.query or parsed.fragment or parsed.username or parsed.password
                or set(settings) & {'credentialProfile', 'accessKeyEnv', 'secretKeyEnv', 'sessionTokenEnv'}):
            raise ValueError('Fixture mode accepts only loopback HTTP and fixed synthetic credentials')
    else:
        region = settings.get('region')
        if region not in REGIONS or settings.get('endpoint') != f'https://s3.{region}.scw.cloud':
            raise ValueError('Use the exact HTTPS Scaleway regional endpoint')
        profile = bool(settings.get('credentialProfile'))
        env = bool(settings.get('accessKeyEnv') and settings.get('secretKeyEnv'))
        if profile == env or (profile and set(settings) & {'accessKeyEnv','secretKeyEnv','sessionTokenEnv'}):
            raise ValueError('Select one explicit credential profile or a pair of environment references')
    return settings


def credentials(settings):
    if settings.get('fixture') is True:
        return FIXTURE_ACCESS, FIXTURE_SECRET, None
    if settings.get('credentialProfile'):
        # Static named profile only: no implicit default, SSO, credential process or metadata fallback.
        parser = configparser.RawConfigParser()
        parser.read(Path.home() / '.aws/credentials')
        profile = settings['credentialProfile']
        try:
            access = parser[profile]['aws_access_key_id']
            secret = parser[profile]['aws_secret_access_key']
            token = parser[profile].get('aws_session_token')
        except KeyError:
            raise ValueError('Named static credential profile is missing or incomplete') from None
    else:
        access = os.environ.get(settings['accessKeyEnv'])
        secret = os.environ.get(settings['secretKeyEnv'])
        token = os.environ.get(settings['sessionTokenEnv']) if settings.get('sessionTokenEnv') else None
        if settings.get('sessionTokenEnv') and not token:
            raise ValueError('Referenced session token is missing')
    if not access or not secret:
        raise ValueError('Referenced S3 credentials are missing')
    return access, secret, token


def client(settings):
    validate_settings(settings)
    access, secret, token = credentials(settings)
    api = boto3.client('s3', region_name=settings['region'], endpoint_url=settings['endpoint'],
        aws_access_key_id=access, aws_secret_access_key=secret, aws_session_token=token,
        config=Config(signature_version='s3v4', s3={'addressing_style': 'path'},
                      connect_timeout=2, read_timeout=3, retries={'total_max_attempts': 1},
                      proxies={}, ignore_configured_endpoint_urls=True))
    expected = urlsplit(settings['endpoint'])
    def check_destination(request, **kwargs):
        actual = urlsplit(request.url)
        if (actual.scheme, actual.netloc) != (expected.scheme, expected.netloc):
            raise Fault('denied')
    api.meta.events.register('before-send.s3', check_destination)
    return api


class Connector(SnapshotConnector):
    def __init__(self, config):
        self.settings = validate_settings(config['s3'])
        self.api = client(self.settings)
        super().__init__(config)

    def read_source(self, path):
        key = self.settings['prefix'] + relative_key(path)
        args = {'Bucket': self.settings['bucket'], 'Key': key}
        response = None
        try:
            head = self.api.head_object(**args)
            size, etag = head.get('ContentLength'), head.get('ETag')
            if not isinstance(size, int) or size < 0 or size > MAX_BYTES or not etag:
                raise Fault('denied')
            version = head.get('VersionId')
            if version and version != 'null':
                args['VersionId'] = version
            response = self.api.get_object(**args, IfMatch=etag)
            if (response.get('ETag') != etag or response.get('ContentLength') != size
                    or ('VersionId' in args and response.get('VersionId') != version)):
                raise Fault('conflict')
            data = response['Body'].read(MAX_BYTES + 1)
            if len(data) != size or len(data) > MAX_BYTES:
                raise Fault('conflict')
            # ETag is an opaque conditional validator, never a Farmy content digest.
            # SnapshotConnector computes SHA-256 and persists the immutable local copy.
            return data
        except ClientError as error:
            code = error.response.get('Error', {}).get('Code', '')
            status = error.response.get('ResponseMetadata', {}).get('HTTPStatusCode')
            if status == 412 or code == 'PreconditionFailed':
                raise Fault('conflict') from None
            if status == 403 or code in ('AccessDenied', 'InvalidAccessKeyId', 'SignatureDoesNotMatch'):
                raise Fault('denied') from None
            if status == 404 or code in ('NoSuchKey', 'NoSuchVersion'):
                raise Fault('not_found') from None
            raise Fault('unavailable') from None
        except (BotoCoreError, OSError, ValueError, KeyError):
            raise Fault('unavailable') from None
        finally:
            if response is not None and 'Body' in response:
                response['Body'].close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True)
    config = json.loads(Path(parser.parse_args().config).read_text())
    try:
        app = Connector(config)
    except (ValueError, Fault, BotoCoreError):
        raise SystemExit('S3 connector configuration or credential reference is invalid; no credentials were logged.') from None
    serve(app)
