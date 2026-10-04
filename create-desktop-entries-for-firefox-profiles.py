#!/usr/bin/env python3

import argparse
import os
import subprocess
import sys
from configparser import ConfigParser, ParsingError
from pathlib import Path


X_KEY = "X-Desktop-Entry-For-Firefox-Profiles"
DESKTOP_ENTRY = f"""
[Desktop Entry]
Version=1.0
Name={{name}} - Firefox Profile
Comment={{path}}
Exec=firefox {{profile_arg}} %u
Icon=firefox
Terminal=false
Type=Application
MimeType=text/html;text/xml;application/xhtml+xml;application/vnd.mozilla.xul+xml;text/mml;x-scheme-handler/http;x-scheme-handler/https;
StartupNotify=true
Categories=Network;WebBrowser;
Keywords=web;browser;internet;
Actions=new-window;new-private-window;
{X_KEY}[Managed]=true

[Desktop Action new-window]
Name=Open a New Window
Exec=firefox {{profile_arg}} --new-window %u

[Desktop Action new-private-window]
Name=Open a New Private Window
Exec=firefox {{profile_arg}} --private-window %u
""".lstrip()


class ArgsNamespace(argparse.Namespace):
    profiles_dir: str
    update: bool


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profiles-dir", "-p", type=str, default="~/.mozilla/firefox")
    parser.add_argument("--update", "-u", action="store_true", default=False)
    args = parser.parse_args(namespace=ArgsNamespace())

    profiles_dir = Path(args.profiles_dir).expanduser()
    profiles_ini = profiles_dir / "profiles.ini"
    if not profiles_ini.exists():
        print(f"{profiles_ini} does not exist!", file=sys.stderr)
        exit(1)

    xdg_data_home = os.environ.get("XDG_DATA_HOME", "~/.local/share")
    applications_dir = Path(xdg_data_home).expanduser() / "applications"
    applications_dir.mkdir(parents=True, exist_ok=True)

    config = ConfigParser()
    config.read(profiles_ini)

    for section_name in config.sections():
        if section_name.startswith("Profile"):
            section = config[section_name]

            if "Name" not in section:
                print(f"\"Name\" not found in \"{section_name}\" section")
                continue
            if "Path" not in section:
                print(f"\"Path\" not found in \"{section_name}\" section")
                continue
            if "IsRelative" not in section:
                print(f"\"IsRelative\" not found in \"{section_name}\" section")
                continue

            name = section["Name"]
            path = Path(section["Path"])
            is_relative = section["IsRelative"] == "1"

            print(f"Got profile: {name=}, {path=}, {is_relative=}")

            desktop_entry_name = f"firefox-profile-{name}.desktop"
            desktop_entry = applications_dir / desktop_entry_name
            if desktop_entry.exists():
                print(f"Entry file exists for profile \"{name}\"")
                entry = ConfigParser()

                try:
                    entry.read(desktop_entry)
                except ParsingError as e:
                    print(f"Failed to parse {desktop_entry}: {e}", file=sys.stderr)
                    continue

                if "Desktop Entry" not in entry:
                    print(f"\"{desktop_entry_name}\" does not contain \"Desktop Entry\" section")
                    continue
                is_managed = entry["Desktop Entry"].get(f"{X_KEY}[Managed]", "false")
                if is_managed != "true":
                    print(f"\"{desktop_entry_name}\" is not managed by this script")
                    continue

            full_path = path if not is_relative else (profiles_dir / name)
            profile_arg = f"-P \"{name}\"" if is_relative else f"-profile \"{full_path}\""

            with open(desktop_entry, "w") as f:
                f.write(DESKTOP_ENTRY.format(
                    name=name,
                    path=full_path,
                    profile_arg=profile_arg,
                ))

            print(f"Created/updated \"{desktop_entry}\"")

    if args.update:
        print("Updating desktop entries database...")
        proc = subprocess.run(
            args=["update-desktop-database", "-v", str(applications_dir)],
            stdout=sys.stdout,
            stderr=sys.stderr,
        )
        if isinstance(proc, subprocess.CalledProcessError):
            print(f"update-desktop-database exited with code {proc.returncode}")
            exit(1)


if __name__ == "__main__":
    main()
