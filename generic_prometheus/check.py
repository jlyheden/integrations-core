# (C) Datadog, Inc. 2016-2017
# All rights reserved
# Licensed under Simplified BSD License (see LICENSE)

import re

from checks import CheckException
from checks.prometheus_check import PrometheusCheck


class GenericPrometheus(PrometheusCheck):
    """
    Scrape any prometheus endpoint for metrics
    """

    def __init__(self, name, init_config, agentConfig, instances=None):
        super(GenericPrometheus, self).__init__(name, init_config, agentConfig, instances)
        self.NAMESPACE = 'generic_prometheus'

        # generic prometheus -> datadog metrics translation table
        self.metrics_mapper = self._instances_to_metrics_mapper(instances)

        # instance specific metrics collection
        self.instance_metrics = self._instance_metrics(instances)

    def _instance_metrics(self, instances):
        kv = {}
        for instance in instances:
            kv[instance.get('prometheus_metrics_url')] = instance.get('prometheus_metrics')
        return kv

    def _instances_to_metrics_mapper(self, instances):
        kv = {}
        for instance in instances:
            for metric in instance.get('prometheus_metrics'):
                if metric not in kv:
                    kv[metric] = self._convert_promethus_metric_to_datadog(metric)
        return kv

    def _convert_promethus_metric_to_datadog(self, m):
        return re.sub(u"_", ".", m)

    def check(self, instance):
        endpoint = instance.get('prometheus_metrics_url')
        if endpoint is None:
            raise CheckException("Unable to find prometheus_metrics_url in config file.")

        if 'labels_mapper' in instance:
            if isinstance(instance['labels_mapper'], dict):
                self.labels_mapper = instance['labels_mapper']
            else:
                self.log.warning("labels_mapper should be a dictionary")

        self.process(endpoint, send_histograms_buckets=False, instance=instance)

    def process_metric(self, message, send_histograms_buckets=True, custom_tags=None, **kwargs):
        """
        patch parent method to look up valid metrics from instance

        Handle a prometheus metric message according to the following flow:
            - search self.metrics_mapper for a prometheus.metric <--> datadog.metric mapping
            - call check method with the same name as the metric
            - log some info if none of the above worked

        `send_histograms_buckets` is used to specify if yes or no you want to send the buckets as tagged values when dealing with histograms.
        """
        try:
            instance = kwargs.get("instance")
            instance_url = instance.get('prometheus_metrics_url')
            if message.name in self.instance_metrics[instance_url]:
                self._submit_metric(self.metrics_mapper[message.name], message, send_histograms_buckets, custom_tags)
            else:
                getattr(self, message.name)(message, **kwargs)
        except AttributeError as err:
            self.log.debug("Unable to handle metric: {} - error: {}".format(message.name, err))
