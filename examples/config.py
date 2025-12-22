import nest

config = nest.Config(
    hostname="vaelixd-pc",
    timezone="Australia/Sydney",
    kernels=["linux-zen", "linux", "linux-lts"],
    bootloader="refind",
    initramfs_generator="mkinitcpio",
)

config.locale = nest.Locale(
    lang="en_US.UTF-8",
    address="en_AU.UTF-8",
)

vaelixd = nest.User(
    username="vaelixd",
    fullname="vaelixd",
    home_dir="/home/vaelixd",
    manage_home=True,
    shell="bash",
    groups=["wheel"],
)

tsp = nest.User(
    username="tsp",
    fullname="The Songbird Project",
    home_dir="/home/project",
    manage_home=False,
    shell="fish",
    groups=["video", "input", "wheel"],
)

config.users = [
    vaelixd,
    tsp,
]

config.emit()
