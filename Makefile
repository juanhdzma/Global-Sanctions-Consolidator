APP_NAME = app/main
ICON_PATH = app/assets/OFAC.ico

install:
	pyinstaller --noconsole --onefile --windowed --icon=$(ICON_PATH) --collect-all openpyxl $(APP_NAME).py

clean:
	rm -rf build dist __pycache__ *.spec

run:
	python $(APP_NAME).py