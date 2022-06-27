hostname="$(hostname).local"
command="\
	cd ~/Desktop/ESRLab_project-team-11/Code/; \
	avahi-resolve-host-name -4 ${hostname} > server_address.txt; \
	./venv/bin/python3 main.py
	"

ssh pi@raspberrypi-ghasem.local ${command}
