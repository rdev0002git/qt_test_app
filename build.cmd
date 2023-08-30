@echo off

call ./.venv/Scripts/activate

pyinstaller --onefile --noconsole --path ./ --exclude-module pyqt5-tools --name qt_test_app ./src/main.py

call ./.venv/Scripts/deactivate

pause