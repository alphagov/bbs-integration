from nose.plugins.attrib import attr
from tests.checks.common import AgentCheckTest
import mock

CONFIG_HEALTHY = {
    'instances': [{
        'url': 'https://localhost:8080',
    }]
}

CONFIG_BAD_STATUS_CODE = {
    'instances': [{
        'url': 'https://localhost:8081',
    }]
}

CONFIG_CANT_CONECT = {
    'instances': [{
        'url': 'https://localhost:8083',
    }]
}
def mocked_requests_post(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    if args[0] == 'https://localhost:8080':
        return MockResponse({}, 200)
    return MockResponse({}, 503)

@attr(requires='bbs')
class TestBbs(AgentCheckTest):
    """Basic Test for bbs integration."""
    CHECK_NAME = 'bbs'

    @mock.patch('requests.post', side_effect=mocked_requests_post)
    def test_healthy_bbs_response(self, mock_requests):
        self.run_check(CONFIG_HEALTHY)

        tags = ['bbs_healthy:yes']
        self.assertMetric('cf.bbs.Healthy', tags=tags, count=1)
        self.assertMetric('cf.bbs.ResponseTime', tags=tags, count=1)

    @mock.patch('requests.post', side_effect=mocked_requests_post)
    def test_bad_status_code_bbs_response(self, mock_requests):
        self.run_check(CONFIG_BAD_STATUS_CODE)

        tags = ['bbs_healthy:no']
        self.assertMetric('cf.bbs.Healthy', tags=tags, count=1)
        self.assertMetric('cf.bbs.ResponseTime', tags=tags, count=1)

    def test_cant_connect_to_bbs_response(self):
        self.run_check(CONFIG_CANT_CONECT)

        tags = ['bbs_healthy:no']
        self.assertMetric('cf.bbs.Healthy', tags=tags, count=1)
