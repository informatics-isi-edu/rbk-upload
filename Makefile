# turn off annoying built-ins
.SUFFIXES:

INSTALL_SCRIPT=./install-script

CLEAN_DIRS=./build ./dist ./*.egg-info

install: conf/config.json force
	python3 ./setup.py install

conf/config.json: conf/config.json.in force
	test -n "$(HOSTNAME)"  # HOSTNAME variable must be set!
	./install-script -M sed -R @@HOST@@=\"$(HOSTNAME)\" -p -D $< $@

bundle-win: install force
	pyinstaller --clean rbk-upload-win.spec

bundle-mac: install force
	pyinstaller --clean rbk-upload-mac.spec

clean: force
	rm -rf $(CLEAN_DIRS)

uninstall: force
	pip uninstall rbk-upload

force:

