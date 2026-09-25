import pathlib
import subprocess

for src, dst in [
    ("/opt/lisenok/deploy/lisenok.service", "/etc/systemd/system/lisenok.service"),
    ("/opt/lisenok/deploy/lisenok-admin.service", "/etc/systemd/system/lisenok-admin.service"),
]:
    text = pathlib.Path(src).read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    pathlib.Path(dst).write_bytes(text)

subprocess.check_call(["systemctl", "daemon-reload"])
subprocess.check_call(["systemctl", "enable", "--now", "lisenok"])
subprocess.check_call(["systemctl", "enable", "--now", "lisenok-admin"])
subprocess.check_call(["systemctl", "enable", "--now", "nginx"])
subprocess.check_call(["systemctl", "restart", "nginx"])

for unit in ("lisenok", "lisenok-admin", "nginx"):
    print(unit, subprocess.check_output(["systemctl", "is-active", unit], text=True).strip())
