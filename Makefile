APP_NAME = app/main
ICON_PATH = app/assets/OFAC.ico

run-win:
	app\venv\Scripts\activate && python $(APP_NAME).py

run-mac:
	source app/venv/bin/activate && python $(APP_NAME).py

clean:
	rm -rf build dist __pycache__ *.spec
