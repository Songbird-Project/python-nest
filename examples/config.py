import nest
from os import path


def genInfo():
    print(nest.nest_autogen)
    with open(path.join(nest.nest_autogen, "genInfo.md"), "w") as file:
        file.write("Hello")


def preBuild():
    pass


def postBuild():
    genInfo()


config = nest.newConfig()

config.hostname = "vaelixd-pc"
config.timezone = "Australia/Sydney"
config.kernels = ["linux-zen", "linux", "linux-lts"]
config.bootloader = "refind"
config.initramfsGenerator = "dracut"
config.preBuild = preBuild
config.postBuild = postBuild

config.locale = nest.Locale(
    lang="en_US.UTF-8",
    address="en_AU.UTF-8",
)

vaelixd = nest.User(
    userName="vaelixd",
    fullName="vaelixd",
    homeDir="/home/vaelixd",
    manageHome=True,
    shell="/bin/bash",
    groups=["wheel"],
)

tsp = nest.User(
    userName="tsp",
    fullName="The Songbird Project",
    homeDir="/home/project",
    manageHome=False,
    shell="/bin/fish",
    groups=["video", "input", "wheel"],
)

config.users = [
    vaelixd,
    tsp,
]

nest.returnConfig(config)
