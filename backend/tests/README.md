# How to Run Tests (Backend)

To ensure all imports work correctly, always run tests from the project root using the following command:

```bash
PYTHONPATH=. pytest backend/tests/ --maxfail=3 --disable-warnings -v
```

- This sets the `PYTHONPATH` to the project root so that imports like `from backend.app import create_app` work as expected.
- You can adjust `--maxfail` as needed.
- Make sure your virtual environment is activated before running tests.

## Troubleshooting
- If you see `ModuleNotFoundError: No module named 'backend'`, double-check you are running the command from the project root and that `PYTHONPATH` is set as above.

---

For more details, see the main README or ask for help.
