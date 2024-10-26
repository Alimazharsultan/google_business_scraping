@echo off

:: Set the directory to where the batch file is located
set "SCRIPT_DIR=%~dp0"

:: Navigate to the directory of the batch file
cd /d "%SCRIPT_DIR%"

:: Check if virtual environment exists
if not exist "%SCRIPT_DIR%env\Scripts\activate.bat" (
    echo Creating virtual environment in the batch file directory...
    python -m virtualenv "%SCRIPT_DIR%env"
    if %errorlevel% neq 0 (
        echo Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo Virtual environment created.
)

:: Activate virtual environment
echo Activating virtual environment...
call "%SCRIPT_DIR%env\Scripts\activate.bat"
if %errorlevel% neq 0 (
    echo Failed to activate virtual environment.
    pause
    exit /b 1
)

:: Install requirements if first time setup
if not exist "%SCRIPT_DIR%env\Scripts\playwright.cmd" (
    echo Installing required packages...
    pip install -r requirements.txt
    playwright install
    if %errorlevel% neq 0 (
        echo Failed to install requirements.
        pause
        exit /b 1
    )
    echo Packages installed.
)

:: Run the Python script
echo Running the gui_scraper script...
python gui_scraper.py

:: Pause to keep the window open
pause
