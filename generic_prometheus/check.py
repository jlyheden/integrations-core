# (C) Datadog, Inc. 2016-2017
# All rights reserved
# Licensed under Simplified BSD License (see LICENSE)

import re
from collections import defaultdict

from checks import CheckException
from checks.prometheus_check import PrometheusCheck


METRIC_TYPES = ['counter', 'gauge']


class GenericPrometheus(PrometheusCheck):
    """
    Scrape any prometheus endpoint for metrics
    """

    def __init__(self, name, init_config, agentConfig, instances=None):
        super(GenericPrometheus, self).__init__(name, init_config, agentConfig, instances)
        self.NAMESPACE = 'generic_prometheus'

        self.metrics_mapper = self._instances_to_metrics_mapper(instances)

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
                self.log.warning("labels_mapper should be a dictionnary")

        self.process(endpoint, send_histograms_buckets=False, instance=instance)

    def _condition_to_service_check(self, metric, sc_name, mapping, tags=None):
        """
        Some metrics contains conditions, labels that have "condition" as name and "true", "false", or "unknown"
        as value. The metric value is expected to be a gauge equal to 0 or 1 in this case.
        For example:

        metric {
          label { name: "condition", value: "true"
          }
          # other labels here
          gauge { value: 1.0 }
        }

        This function evaluates metrics containing conditions and sends a service check
        based on a provided condition->check mapping dict
        """
        if bool(metric.gauge.value) is False:
            return  # Ignore if gauge is not 1
        for label in metric.label:
            if label.name == 'condition':
                if label.value in mapping:
                    self.service_check(sc_name, mapping[label.value], tags=tags)
                else:
                    self.log.debug("Unable to handle %s - unknown condition %s" % (sc_name, label.value))

    def _extract_label_value(self, name, labels):
        """
        Search for `name` in labels name and returns
        corresponding value.
        Returns None if name was not found.
        """
        for label in labels:
            if label.name == name:
                return label.value
        return None

    def _format_tag(self, name, value):
        """
        Lookups the labels_mapper table to see if replacing the tag name is
        necessary, then returns a "name:value" tag string
        """
        return '%s:%s' % (self.labels_mapper.get(name, name), value)

    def _label_to_tag(self, name, labels, tag_name=None):
        """
        Search for `name` in labels name and returns corresponding tag string.
        Tag name is label name if not specified.
        Returns None if name was not found.
        """
        value = self._extract_label_value(name, labels)
        if value:
            return self._format_tag(tag_name or name, value)
        else:
            return None

    def _trim_job_tag(self, name):
        """
        Trims suffix of job names if they match -(\d{4,10}$)
        """
        pattern = "(-\d{4,10}$)"
        return re.sub(pattern, '', name)

    # Labels attached: namespace, pod, phase=Pending|Running|Succeeded|Failed|Unknown
    # The phase gets not passed through; rather, it becomes the service check suffix.
