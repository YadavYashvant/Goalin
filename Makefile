.PHONY: help install install-dev uninstall test clean build service-install service-start service-stop service-status lint format

help:
	@echo "Goalin - Makefile Commands"
	@echo "=========================="
	@echo "install          - Install Goalin for the current user"
	@echo "install-dev      - Install in development mode"
	@echo "uninstall        - Uninstall Goalin"
	@echo "test             - Run installation tests"
	@echo "clean            - Remove build artifacts"
	@echo "build            - Build distribution packages"
	@echo "service-install  - Install and enable systemd service"
	@echo "service-start    - Start the Goalin daemon"
	@echo "service-stop     - Stop the Goalin daemon"
	@echo "service-status   - Check daemon status"
	@echo "lint             - Run code linting"
	@echo "format           - Format code with black"

install:
	pip install --user .
	@echo ""
	@echo "Installation complete!"
	@echo "Run 'make service-install' to set up the daemon"

install-dev:
	pip install --user -e .
	pip install --user pytest pylint black
	@echo ""
	@echo "Development installation complete!"

uninstall:
	@echo "Stopping and disabling service..."
	-systemctl --user stop goalin.service 2>/dev/null
	-systemctl --user disable goalin.service 2>/dev/null
	@echo "Removing service file..."
	-rm -f ~/.config/systemd/user/goalin.service
	systemctl --user daemon-reload
	@echo "Uninstalling package..."
	pip uninstall -y goalin
	@echo "Removing desktop entry..."
	-rm -f ~/.local/share/applications/goalin.desktop
	-update-desktop-database ~/.local/share/applications/ 2>/dev/null
	@echo ""
	@echo "Goalin has been uninstalled."
	@echo "To remove data, run: rm -rf ~/.local/share/goalin ~/.config/goalin ~/.cache/goalin"

test:
	python3 test_installation.py

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

build: clean
	python3 setup.py sdist bdist_wheel

service-install:
	@echo "Installing systemd service..."
	mkdir -p ~/.config/systemd/user/
	cp goalin.service ~/.config/systemd/user/
	systemctl --user daemon-reload
	systemctl --user enable goalin.service
	@echo ""
	@echo "Service installed and enabled!"
	@echo "Run 'make service-start' to start it now"

service-start:
	systemctl --user start goalin.service
	@echo "Service started. Check status with 'make service-status'"

service-stop:
	systemctl --user stop goalin.service
	@echo "Service stopped."

service-status:
	systemctl --user status goalin.service

lint:
	@echo "Running pylint..."
	pylint src/goalin/*.py || true

format:
	@echo "Formatting code with black..."
	black src/goalin/
	@echo "Done!"

.DEFAULT_GOAL := help
