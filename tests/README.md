# E2E tests

Before running the End-to-End tests for the container, make sure that you installed docker and the development requirements in your python environment.

## Run the testcases

To perform automatic E2E testing, go to the `/tests` directory and run the following commands:

```bash
$ cd tests
$ pytest
```

To develop for this test cases, you can stage the environment using the following commands:

```bash
$ cd tests
$ python3 cli.py create-scenario-1
create containers for scenario 1...
containers for scenario 1 created
# destroy it using the following command
$ python3 cli.py destroy-scenario-1
```


```bash
$ cd tests
$ python3 cli.py create-scenario-2
create containers for scenario 2...
containers for scenario 2 created
# destroy it using the following command
$ python3 cli.py destroy-scenario-2
```

## Scenario 1 (Hub-and-Spoke) test case

The following diagram describes the structure of the test infrastructure for scenario 1.

![](../docs/scenarios/scenario_1/scenario_1.drawio.svg)

## Scenario 1 (Partial Mesh with Multiple Temporary Hubs) test case

The following diagram describes the structure of the test infrastructure for scenario 2.
