from dataclasses import asdict, dataclass
from inspect import getsource
from os import getenv, mkdir
from types import FunctionType
from typing import Optional

@dataclass
class NestConfig:
    hostname: str
    kernel: str = "linux"
    bootloader: str = "limine"
    initramfsGenerator: str = "booster"
    preBuild: Optional[FunctionType] = None
    postBuild: Optional[FunctionType] = None

os_info = {}
nest_gen_root = getenv("NEST_GEN_ROOT") or ""

def newConfig() -> NestConfig:
    with open("/etc/os-release", "r") as os_release:
        for line in os_release:
            line = line.strip()
            if not line or "=" not in line:
                continue
            key, _, value = line.partition("=")
            value = value.strip("'\"")
            os_info[key.lower()] = value

    config = NestConfig(
        hostname=os_info["id"],
    )

    return config

def returnConfig(config: NestConfig):
    configDict = asdict(config)
    scsvConfig = ""

    for key in configDict:
        value = __checkValue(key, configDict[key])
        if value == False:
            continue
        scsvConfig += key + "," + value + "\n"

    print(scsvConfig)

def __checkValue(key: str, value):
    if key == "hostname":
        return str(value).replace(" ", "-")
    if key == "preBuild" or key == "postBuild":
        if value != None:
            buildFunc = [getsource(value), value.__name__]
            __generateBuildFiles(buildFunc, key)

        return False
    else:
        return value

def __generateBuildFiles(buildFunc: list[str], buildType: str):
    mkdir(nest_gen_root)

    with open(nest_gen_root + buildType + ".py", "w") as file:
            file.writelines([buildFunc[0] + "\n", buildFunc[1] + "()"])
