from dataclasses import asdict, dataclass
from os import getenv, path
from pathlib import Path
from json import dump, dumps


@dataclass
class _LocaleConfig:
    lang: str
    address: str
    identification: str
    measurement: str
    monetary: str
    name: str
    numeric: str
    paper: str
    telephone: str
    time: str


@dataclass
class _UserConfig:
    username: str
    fullname: str
    home_dir: str
    shell: str
    manage_home: bool
    groups: list[str]


@dataclass
class _SystemConfig:
    hostname: str
    timezone: str
    locale: dict
    kernels: list[str]
    users: list[dict]
    bootloader: str
    initramfs_generator: str
    pre_build: str
    post_build: str


class Locale:
    def __init__(
        self,
        lang: str = "",
        address: str = "",
        identification: str = "",
        measurement: str = "",
        monetary: str = "",
        name: str = "",
        numeric: str = "",
        paper: str = "",
        telephone: str = "",
        time: str = "",
    ):
        if not lang and not address:
            address = "en_US.UTF-8"

        self.lang = lang or address
        self.address = address or lang
        self.identification = identification or address
        self.measurement = measurement or address
        self.monetary = monetary or address
        self.name = name or address
        self.numeric = numeric or address
        self.paper = paper or address
        self.telephone = telephone or address
        self.time = time or address


class User:
    def __init__(
        self,
        username: str = "",
        fullname: str = "",
        home_dir: str = "",
        shell: str = "",
        manage_home: bool = False,
        groups: list[str] = [],
    ):
        if not username and not fullname:
            fullname = "User"

        self.username = username if username else fullname.replace(" ", "-").lower()
        self.fullname = fullname if fullname else username
        self.home_dir = home_dir if home_dir else f"/home/{username}"
        self.shell = shell or "nu"
        self.manage_home = manage_home or False
        self.groups = groups

        if not self.username in self.groups:
            self.groups = [username] + self.groups


class Config:
    def __init__(
        self,
        hostname: str = "",
        timezone: str = "",
        locale: Locale = Locale(),
        kernels: list[str] = [],
        users: list[User] = [],
        bootloader: str = "",
        initramfs_generator: str = "",
        pre_build: str = "",
        post_build: str = "",
    ):
        self.hostname = hostname.replace(" ", "-").lower() or "my-pc"
        self.timezone = timezone or "Etc/UTC"
        self.locale = locale or Locale()
        self.kernels = kernels or ["linux"]
        self.users = users or [User()]
        self.bootloader = bootloader.lower() or "grub"
        self.initramfs_generator = initramfs_generator.lower() or "dracut"
        self.pre_build = pre_build
        self.post_build = post_build

    def emit(self):
        locale = asdict(
            _LocaleConfig(
                self.locale.lang,
                self.locale.address,
                self.locale.identification,
                self.locale.measurement,
                self.locale.monetary,
                self.locale.name,
                self.locale.numeric,
                self.locale.paper,
                self.locale.telephone,
                self.locale.time,
            )
        )
        users = []
        for user in self.users:
            user_config = _UserConfig(
                user.username,
                user.fullname,
                user.home_dir,
                user.shell,
                user.manage_home,
                user.groups,
            )
            users.append(user_config)

        config = _SystemConfig(
            self.hostname,
            self.timezone,
            locale,
            self.kernels,
            users,
            self.bootloader,
            self.initramfs_generator,
            self.pre_build,
            self.post_build,
        )

        nest_autogen = getenv("NEST_AUTOGEN") or ""

        if not path.exists(nest_autogen) and nest_autogen:
            Path(nest_autogen).mkdir(parents=True)

        with open(path.join(nest_autogen, "config.json"), "w") as file:
            dump(asdict(config), file, indent=4)

        print(dumps(asdict(config), indent=4))
