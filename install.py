import argparse
import os
import shutil
import stat
from pathlib import Path


FILENAME = "create-desktop-entries-for-firefox-profiles"


class ArgsNamespace(argparse.Namespace):
    profiles_dir: str


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profiles-dir", "-p", type=str, default="~/.mozilla/firefox")
    args = parser.parse_args(namespace=ArgsNamespace())

    profiles_dir = Path(args.profiles_dir).expanduser()

    xdg_data_home = os.environ.get("XDG_DATA_HOME", "~/.local/share")
    systemd_dir = Path(xdg_data_home).expanduser() / "systemd" / "user"
    systemd_dir.mkdir(parents=True, exist_ok=True)

    home = os.environ.get("HOME", "~")
    local_bin_dir = Path(home).expanduser() / ".local" / "bin"

    script_out_path = local_bin_dir / f"{FILENAME}.py"
    service_unit_path = systemd_dir / f"{FILENAME}.service"
    path_unit_path = systemd_dir / f"{FILENAME}.path"

    print(f"Writing {script_out_path} ...")
    shutil.copy(f"{FILENAME}.py", script_out_path)
    script_out_path.chmod(script_out_path.stat().st_mode | stat.S_IXUSR)

    print(f"Writing {service_unit_path} ...")
    with open(f"{FILENAME}.service", "r") as in_file, open(service_unit_path, "w") as out_file:
        content = in_file.read()
        out_file.write(content.format(profiles_dir=profiles_dir, script_path=script_out_path.absolute()))

    print(f"Writing {path_unit_path} ...")
    with open(f"{FILENAME}.path", "r") as in_file, open(path_unit_path, "w") as out_file:
        content = in_file.read()
        out_file.write(content.format(profiles_dir=profiles_dir))


if __name__ == "__main__":
    main()
