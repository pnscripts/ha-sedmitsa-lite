# Sedmitsa Lite by PN Scripts
PY ?= python3
.PHONY: test dist images clean
# Needs a venv with pytest-homeassistant-custom-component (see README, "Tests").
test:
	$(PY) -m pytest -q -p no:cacheprovider tests
# The asset HACS downloads (hacs.json: zip_release, filename sedmitsa_lite.zip).
dist: clean
	mkdir -p dist
	cd custom_components/sedmitsa_lite && zip -qr -X ../../dist/sedmitsa_lite.zip . -x '__pycache__/*'
	@ls -la dist
images:
	node tools/render.mjs tools/images.mjs
clean:
	rm -rf build dist
