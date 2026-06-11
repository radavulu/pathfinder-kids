@echo off
REM Home Kumon — one-command launcher for Windows.
cd /d "%~dp0"

REM The app and LM Studio are local - bypass any corporate proxy for local traffic.
set NO_PROXY=localhost,127.0.0.1,::1
set no_proxy=localhost,127.0.0.1,::1

if not exist ".venv" (
  echo Creating virtual environment...
  python -m venv .venv
)

set VENV_PY=.venv\Scripts\python.exe
if not exist "%VENV_PY%" (
  echo Virtual environment is broken. Remove .venv and run again.
  exit /b 1
)

"%VENV_PY%" -m pip --version >nul 2>&1
if errorlevel 1 (
  echo Bootstrapping pip in virtual environment...
  "%VENV_PY%" -m ensurepip --upgrade
)

REM Behind a corporate proxy (e.g. iboss) pip can't reach PyPI? Set PIP_PROXY first, e.g.:
REM   set PIP_PROXY=http://127.0.0.1:8009
REM When a proxy is set we also trust PyPI hosts (SSL inspection re-signs certs, which pip would reject).
set PIP_ARGS=
if not "%PIP_PROXY%"=="" set PIP_ARGS=--proxy %PIP_PROXY%
if not "%PIP_PROXY%"=="" set PIP_ARGS=%PIP_ARGS% --trusted-host pypi.org --trusted-host files.pythonhosted.org --trusted-host pypi.python.org
if not "%PIP_TRUSTED%"=="" set PIP_ARGS=%PIP_ARGS% --trusted-host pypi.org --trusted-host files.pythonhosted.org --trusted-host pypi.python.org

echo Installing dependencies...
"%VENV_PY%" -m pip install --quiet %PIP_ARGS% --upgrade pip
"%VENV_PY%" -m pip install --quiet %PIP_ARGS% -r requirements.txt

if "%HOMEKUMON_HOST%"=="" set HOMEKUMON_HOST=127.0.0.1
REM Default port — override for one run: set HOMEKUMON_PORT=8890
if "%HOMEKUMON_PORT%"=="" set HOMEKUMON_PORT=8700
set PORT=%HOMEKUMON_PORT%

start "" /B cmd /c "timeout /t 2 /nobreak >nul && start http://%HOMEKUMON_HOST%:%PORT%"
echo Starting Home Kumon at http://%HOMEKUMON_HOST%:%PORT%  (press Ctrl+C to stop)
"%VENV_PY%" -m uvicorn app.main:app --host %HOMEKUMON_HOST% --port %PORT%
