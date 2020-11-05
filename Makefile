lint:
	isort -rc heybrochecklog/ tests/
#	black heybrochecklog/ tests/

tests:
#	black --check heybrochecklog/ tests/
	python3 -m pytest

clean:
	rm -rf build/ dist/ *.egg-info
	find . -type d -name "__pycache__" -exec rm -r "{}" \;

.PHONY: lint tests clean
