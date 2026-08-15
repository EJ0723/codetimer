# codetimer

A simple utility to monitor when specific applications (e.g., VS Code, Zed) are opened or closed on Windows, using WMI.

**Author:** Edward Joshwin Oña

## Development Workflow

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd codetimer
   ```

2. **Create and activate a virtual environment** (Windows PowerShell)
   ```powershell
   virtualenv -p 3.12.5 venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Run the script**
   ```powershell
   python .\main.py
   ```

5. **Update dependencies**
   After installing a new package:
   ```powershell
   pip freeze > requirements.txt
   ```

6. **Linting / Formatting (optional)**
   If you add linting tools later, you can run them with:
   ```powershell
   pip install -r requirements-dev.txt   # if you create a dev file
   # e.g., flake8 . or black .
   ```

## Notes
- The script relies on the `wmi` package, which is Windows‑only. Development and execution must be done on a Windows Python interpreter.
- Keep the virtual environment out of version control (`.gitignore` should contain `venv/`).

## License
MIT – feel free to use and modify.