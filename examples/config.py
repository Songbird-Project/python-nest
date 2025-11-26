import nest


def genInfo():
    with open(f"{nest.nest_autogen}genInfo.md", "w") as file:
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
    fullName="vaelixd",
    userName="vaelixd",
    homeDir="/home/vaelixd",
    manageHome=True,
    groups=["wheel"],
)

dds = nest.User(
    userName="dds",
)

config.users = [
    vaelixd,
    dds,
]

nest.returnConfig(config)
