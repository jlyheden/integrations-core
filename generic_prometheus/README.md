# Generic Prometheus Scraper

## Overview

Get metrics from any prometheus metrics endpoint in real time to:

* Visualize and monitor your application

## Setup
### Installation

Install the `dd-check-generic_prometheus` package manually or with your favorite configuration manager

### Configuration

Edit the `generic_prometheus.yaml` file to point to your server and port, set the metrics to collect

### Validation

When you run `datadog-agent info` you should see something like the following:

    Checks
    ======

        generic_prometheus
        -----------
          - instance #0 [OK]
          - Collected 39 metrics, 0 events & 7 service checks

## Compatibility

The generic_prometheus check is compatible with all major platforms

## Data Collected
### Metrics
None, since it is up to the application to decide the metrics

### Events
The generic_prometheus check does not include any event at this time.

### Service Checks
The generic_prometheus check does not include any service check at this time.

## Troubleshooting

If you have any questions about Datadog or a use case our [Docs](https://docs.datadoghq.com/) didn’t mention, we’d love to help! Here’s how you can reach out to us:

### Visit the Knowledge Base

Learn more about what you can do in Datadog on the [Support Knowledge Base](https://datadog.zendesk.com/agent/).

### Web Support

Messages in the [event stream](https://app.datadoghq.com/event/stream) containing **@support-datadog** will reach our Support Team. This is a convenient channel for referencing graph snapshots or a particular event. In addition, we have a livechat service available during the day (EST) from any page within the app.

### By Email

You can also contact our Support Team via email at [support@datadoghq.com](mailto:support@datadoghq.com).

### Over Slack

Reach out to our team and other Datadog users on [Slack](http://chat.datadoghq.com/).

## Further Reading
Learn more about infrastructure monitoring and all our integrations on [our blog](https://www.datadoghq.com/blog/)