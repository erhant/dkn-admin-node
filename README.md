<p align="center">
  <img src="https://raw.githubusercontent.com/firstbatchxyz/dria-js-client/master/logo.svg" alt="logo" width="142">
</p>

<p align="center">
  <h1 align="center">
    Dria Admin Node
  </h1>
  <p align="center">
    <i>Dria Admin Node controller layer of Dria Knowledge Network</i>
  </p>
</p>


## About

A **Dria Admin Node** is a controller layer of the Dria Knowledge Network. It's purpose is to manage the compute nodes, assign tasks, and reward them for providing correct results.

### Functions

- **Monitor**: Admin node broadcasts heartbeat messages at a set interval, compute nodes respond to these to be included in the list of available nodes for task assignment.
- **Publisher**: Admin node publishes tasks to the network, compute nodes receive these tasks and process them.
- **Aggregator**: Admin node aggregates the results from compute nodes, and rewards them for providing correct results.

### Usage

The admin node can be run with the following command:

```sh
python run.py
```

### Disabling Tasks

Tasks can be disabled by providing the task name as an environment variable to the executable.

For example, to disable the publisher and aggregator tasks:
```sh
PUBLISHER_WORKERS=0 AGGREGATOR_WORKERS=0 python run.py
```

### Testing

TODO: describe testing
