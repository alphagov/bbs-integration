import time
import requests

from checks import AgentCheck
from hashlib import md5

EVENT_TYPE = SOURCE_TYPE_NAME = 'bbs'


class BbsCheck(AgentCheck):

    def __init__(self, name, init_config, agentConfig, instances=None):
        AgentCheck.__init__(self, name, init_config, agentConfig, instances)

    def check(self, instance):
        if 'url' not in instance:
            self.log.info("Skipping instance, no url found.")
            return

        # Load values from the instance config
        url = instance['url']
        default_timeout = self.init_config.get('default_timeout', 5)
        timeout = float(instance.get('timeout', default_timeout))

        # Use a hash of the URL as an aggregation key
        aggregation_key = md5(url).hexdigest()

        # Cert paths are taken from https://github.com/cloudfoundry/diego-release/blob/d52495a551e0ce15eadd21eb4460af9dfacc7148/jobs/cfdot/templates/setup.erb#L5
        client_cert = instance.get('client_cert','/var/vcap/jobs/cfdot/config/certs/bbs/client.crt')
        client_key = instance.get('client_key','/var/vcap/jobs/cfdot/config/certs/bbs/client.key')
        ca_cert = instance.get('ca_cert','/var/vcap/jobs/cfdot/config/certs/bbs/ca.crt')

        # Check the URL
        start_time = time.time()
        try:
            r = requests.post(url, timeout=timeout, cert=(client_cert, client_key), verify=ca_cert)
            end_time = time.time()
        except requests.exceptions.RequestException as e:
            self.connection_event(url, e, aggregation_key)
            self.gauge('cf.bbs.Healthy', 0, tags=['bbs_healthy:no'])
            return

        timing = end_time - start_time
        if r.status_code != 200:
            self.status_code_event(url, r, aggregation_key)
            self.gauge('cf.bbs.ResponseTime', timing, tags=['bbs_healthy:no'])
            self.gauge('cf.bbs.Healthy', 0, tags=['bbs_healthy:no'])
            return

        self.gauge('cf.bbs.ResponseTime', timing, tags=['bbs_healthy:yes'])
        self.gauge('cf.bbs.Healthy', 1, tags=['bbs_healthy:yes'])

    def connection_event(self, url, error, aggregation_key):
        self.event({
            'timestamp': int(time.time()),
            'event_type': 'bbs_check',
            'msg_title': 'Connection aborted',
            'msg_text': '%s connection aborted. %s.' % (url, error),
            'aggregation_key': aggregation_key
        })

    def status_code_event(self, url, r, aggregation_key):
        self.event({
            'timestamp': int(time.time()),
            'event_type': 'bbs_check',
            'msg_title': 'Invalid reponse code for %s' % url,
            'msg_text': '%s returned a status of %s' % (url, r.status_code),
            'aggregation_key': aggregation_key
        })
