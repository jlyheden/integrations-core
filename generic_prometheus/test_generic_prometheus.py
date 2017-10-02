# (C) Datadog, Inc. 2016
# All rights reserved
# Licensed under Simplified BSD License (see LICENSE)

# stdlib
import mock
import os

# project
from tests.checks.common import AgentCheckTest
from nose.plugins.attrib import attr

NAMESPACE = 'generic_prometheus'


@attr(requires='generic_prometheus')
class TestGenericPrometheus(AgentCheckTest):

    CHECK_NAME = 'generic_prometheus'

    PROMETHEUS_METRICS = [
        'jvm_buffer_count'
    ]

    METRICS = [
        NAMESPACE + '.jvm.buffer.count'
    ]

    # what is this?
    ZERO_METRICS = [
        NAMESPACE + '.deployment.replicas_unavailable',
        NAMESPACE + '.deployment.paused',
        NAMESPACE + '.daemonset.misscheduled',
        NAMESPACE + '.container.terminated',
        NAMESPACE + '.container.waiting',
    ]

    def assertMetricNotAllZeros(self, metric_name):
        for mname, ts, val, mdata in self.metrics:
            if mname == metric_name:
                if val != 0:
                    return True
        raise AssertionError("All metrics named %s have 0 value." % metric_name)

    @mock.patch('checks.prometheus_check.PrometheusCheck.poll')
    def test__update_generic_prometheus_metrics(self, mock_poll):
        f_name = os.path.join(os.path.dirname(__file__), 'ci', 'fixtures', 'prometheus', 'protobuf.text')
        with open(f_name, 'rb') as f:
            mock_poll.return_value = ('text/plain', f.read())

        config = {
            'instances': [{
                'host': 'foo',
                'prometheus_metrics_url': 'http://foo',
                'prometheus_metrics': self.PROMETHEUS_METRICS
            }]
        }

        self.run_check(config)

        for metric in self.METRICS:
            self.assertMetric(metric)
            if metric not in self.ZERO_METRICS:
                self.assertMetricNotAllZeros(metric)

        self.assert_resourcequota()

    def assert_resourcequota(self):
        """ The metric name is created dynamically so we just check some exist. """
        for m in self.metrics:
            if 'kubernetes_state.resourcequota.' in m[0]:
                return True
        return False
