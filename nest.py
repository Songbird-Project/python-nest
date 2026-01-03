from dataclasses import asdict, dataclass, field
import json
from os import getenv, path
from pathlib import Path
from json import dump, dumps
from typing import Optional


@dataclass
class Locale:
    lang: str = ""
    address: str = ""
    identification: str = ""
    measurement: str = ""
    monetary: str = ""
    name: str = ""
    numeric: str = ""
    paper: str = ""
    telephone: str = ""
    time: str = ""

    def __post_init__(self):
        default = self.address or "en_US.UTF-8"

        self.lang = self.lang or default
        self.address = self.address or default
        self.identification = self.identification or default
        self.measurement = self.measurement or default
        self.monetary = self.monetary or default
        self.name = self.name or default
        self.numeric = self.numeric or default
        self.paper = self.paper or default
        self.telephone = self.telephone or default
        self.time = self.time or default


@dataclass
class User:
    username: str = ""
    fullname: str = ""
    home_dir: str = ""
    shell: str = "nu"
    manage_home: bool = False
    groups: list[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.username and not self.fullname:
            self.fullname = "User"

        if not self.username:
            self.username = self.fullname.replace(" ", "-").lower()
        if not self.fullname:
            self.fullname = self.username

        if not self.home_dir:
            self.home_dir = f"/home/{self.username}"

        if not self.username in self.groups:
            self.groups.insert(0, self.username)


@dataclass
class Config:
    hostname: str = ""
    timezone: str = ""
    locale: Locale = field(default_factory=Locale)
    kernels: list[str] = field(default_factory=list)
    users: list[User] = field(default_factory=list)
    bootloader: str = ""
    initramfs_generator: str = ""
    pre_build: str = ""
    post_build: str = ""

    def __post_init__(self):
        self.hostname = self.hostname.replace(" ", "-").lower() or "my-pc"
        self.timezone = self.timezone or "Etc/UTC"
        self.locale = self.locale or Locale()
        self.kernels = self.kernels or ["linux"]
        self.users = self.users or [User()]
        self.bootloader = self.bootloader.lower() or "grub"
        self.initramfs_generator = self.initramfs_generator.lower() or "dracut"

    def to_dict(self):
        return {
            "hostname": self.hostname,
            "timezone": self.timezone,
            "locale": asdict(self.locale),
            "kernels": self.kernels,
            "users": [asdict(user) for user in self.users],
            "bootloader": self.bootloader,
            "initramfs_generator": self.initramfs_generator,
            "pre_build": self.pre_build,
            "post_build": self.post_build,
        }

    def emit(self, stdout: Optional[bool] = False, output_dir: Optional[str] = ""):
        config = self.to_dict()

        output_dir = output_dir or getenv("NEST_AUTOGEN", "")

        if output_dir:
            config_path = Path(output_dir)
            config_path.mkdir(parents=True, exist_ok=True)

            config_file = config_path / "config.json"
            with config_file.open("w") as file:
                json.dump(config, file, indent=4)

        if stdout:
            print(dumps(config, indent=4))

        return config
