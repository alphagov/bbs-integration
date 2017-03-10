# Bbs Integration

## Overview

Get metrics from bbs service in real time to:

* Visualize and monitor bbs states
* Be notified about bbs failovers and events.

## Installation

Install the `dd-check-bbs` package manually or with your favorite configuration manager

## Configuration

Edit the `bbs.yaml` file to point to your server and port, set the masters to monitor

## Validation

When you run `datadog-agent info` you should see something like the following:

    Checks
    ======

        bbs
        -----------
          - instance #0 [OK]
          - Collected 39 metrics, 0 events & 7 service checks

## Compatibility

The bbs check is compatible with all major platforms
