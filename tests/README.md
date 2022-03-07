# E2E tests

To perform automatic E2E testing, go to the `/tests` directory and run the following commands:

```bash
python3 cli.py create-scenario-1
sleep 60
pytest
python3 cli.py destroy-scenario-1
```
