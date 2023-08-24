# Checkers for Icinga

## Setup

```bash
sudo visudo
#add next line to the end
nagios ALL=(ALL:ALL) NOPASSWD: /usr/bin/mwcap-info

/bin/bash -c "$(curl -fsSL https://raw.github.com/artrurkovalenkotivo/monitoring/main/setup.sh)"
```
