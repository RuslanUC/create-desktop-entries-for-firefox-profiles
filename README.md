# Small script (+systemd service) to create desktop entries for firefox profiles

### Usage
```shell
usage: create-desktop-entries-for-firefox-profiles.py [-h] [--profiles-dir PROFILES_DIR] [--update]

options:
  -h, --help            show this help message and exit
  --profiles-dir PROFILES_DIR, -p PROFILES_DIR  # .mozilla/firefox by default
  --update, -u  # run update-desktop-database after profiles were processed
```

### Install as systemd service
This will install `create-desktop-entries-for-firefox-profiles.py` to `~/.local/bin`, `create-desktop-entries-for-firefox-profiles.service` and `create-desktop-entries-for-firefox-profiles.path` to `~/.local/share/systemd/system`

You can specify custom firefox profiles directory via `--profiles-dir` argument.

```shell
python install.py
```

Then, reload systemd and enable service and path units:
```shell
systemctl --user daemon-reload
systemctl --user enable --now create-desktop-entries-for-firefox-profiles.{path,service}
```
