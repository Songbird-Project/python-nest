from dataclasses import asdict, dataclass, field
from inspect import getsource
import inspect
from os import getenv, path
from types import FunctionType
from typing import List, Optional
from pathlib import Path
import ast


@dataclass
class Locale:
    lang: str = "en_US.UTF-8"
    address: str = ""
    identification: str = ""
    measurement: str = ""
    monetary: str = ""
    name: str = ""
    numeric: str = ""
    paper: str = ""
    telephone: str = ""
    time: str = ""


@dataclass
class User:
    userName: str = "user"
    fullName: str = ""
    homeDir: str = ""
    shell: str = "/bin/nu"
    manageHome: bool = False
    groups: List[str] = field(default_factory=list)


@dataclass
class SystemConfig:
    hostname: str
    timezone: str = "Etc/UTC"
    locale: Locale = field(default_factory=Locale)
    kernels: List[str] = field(default_factory=list)
    users: List[User] = field(default_factory=list)
    bootloader: str = "limine"
    initramfsGenerator: str = "booster"
    preBuild: Optional[FunctionType] = None
    postBuild: Optional[FunctionType] = None


os_info = {}
nest_autogen = getenv("NEST_AUTOGEN") or ""


def newConfig() -> SystemConfig:
    with open("/etc/os-release", "r") as os_release:
        for line in os_release:
            line = line.strip()
            if not line or "=" not in line:
                continue
            key, _, value = line.partition("=")
            value = value.strip("'\"")
            os_info[key.lower()] = value

    config = SystemConfig(
        hostname=os_info["id"],
        kernels=["linux"],
    )

    return config


def returnConfig(config: SystemConfig):
    configDict = asdict(config)

    if not path.exists(nest_autogen) and nest_autogen:
        Path(nest_autogen).mkdir(parents=True)

    if configDict["locale"]:
        print("Generating locale config...", end=" ")
        __generateLocaleConfig(config.locale)
        configDict.pop("locale")
        print("done")

    if configDict["users"]:
        print("Generating user config...", end=" ")
        __generateUserConfig(config.users)
        configDict.pop("users")
        print("done")

    if configDict["preBuild"]:
        print("Generating preBuild...", end=" ")
        __generateBuildFiles(configDict["preBuild"], "preBuild")
        configDict.pop("preBuild")
        print("done")

    if configDict["postBuild"]:
        print("Generating postBuild...", end=" ")
        __generateBuildFiles(configDict["postBuild"], "postBuild")
        configDict.pop("postBuild")
        print("done")

    print("Generating system config...", end=" ")
    __generateSystemConfig(configDict)
    print("done")


def __checkValue(key: str, value):
    if key == "hostname":
        return str(value).replace(" ", "-").lower()
    elif isinstance(value, list):
        if key == "kernels":
            return str.join(",", value)
    else:
        return value


def __getDependencies(func: FunctionType):
    source = inspect.getsource(func)
    module = inspect.getmodule(func)

    tree = ast.parse(source)
    calledFunctions = set()
    imports = set()
    usedModules = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                calledFunctions.add(node.func.id)
            elif isinstance(node.func, ast.Attribute) and isinstance(
                node.func.value, ast.Name
            ):
                usedModules.add(node.func.value.id)
        if isinstance(node, ast.Name):
            usedModules.add(node.id)
        elif isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
            usedModules.add(node.value.id)

    try:
        if module != None:
            moduleSource = inspect.getsource(module)
            moduleTree = ast.parse(moduleSource)

            for node in ast.walk(moduleTree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        usedImport = alias.asname if alias.asname else alias.name
                        if (usedImport or alias.name) in usedModules:
                            imports.add(f"import {alias.name}")
                elif isinstance(node, ast.ImportFrom):
                    moduleName = node.module or ""
                    usedImports = []

                    for alias in node.names:
                        usedImport = alias.asname if alias.asname else alias.name
                        if usedImport in (usedModules or calledFunctions):
                            usedImports.append(alias.name)

                    if usedImports:
                        imports.add(
                            f"from {moduleName} import {str.join(",", usedImports)}"
                        )
    except:
        pass

    localFunctions = {}
    for funcName in calledFunctions:
        if hasattr(module, funcName):
            funcObject = getattr(module, funcName)

            if callable(funcObject) and not inspect.isbuiltin(funcObject):
                try:
                    funcSource = inspect.getsource(funcObject)
                    localFunctions[funcName] = funcSource

                    if inspect.isfunction(funcObject):
                        deps = __getDependencies(funcObject)
                        imports.update(deps["imports"])
                        localFunctions.update(deps["functions"])
                except (OSError, TypeError):
                    pass

    return {"imports": imports, "functions": localFunctions}


def __generateBuildFiles(buildFunc: FunctionType, buildType: str):
    module = __getDependencies(buildFunc)
    deps = module["imports"]
    functions = module["functions"]

    with open(path.join(nest_autogen, f"{buildType}.py"), "w") as file:
        if deps:
            for dep in sorted(deps):
                file.write(f"{dep}\n")

            file.write("\n")

        if functions:
            for _, func in functions.items():
                file.write(func)

            file.write("\n")

        file.write(getsource(buildFunc))
        file.write("\n")
        file.write(f"{buildFunc.__name__}()")


def __generateUserConfig(users: List[User]):
    usersSCSV = """#@valuePrecedence,false
#@strictMode,false

"""

    for user in users:
        user.userName = user.userName if user.userName else user.fullName.lower()
        user.fullName = user.fullName if user.fullName else user.userName
        user.homeDir = user.homeDir if user.homeDir else f"/home/{user.userName}"

        if not user.userName in user.groups:
            user.groups = [user.userName] + user.groups

        usersSCSV += f"""|{user.userName},fullName,{user.fullName}
,homeDir,{user.homeDir}
,manageHome,{str(user.manageHome).lower()}
,shell,{user.shell}
,groups,{str.join(",", user.groups)}

"""

    with open(path.join(nest_autogen, "users.scsv"), "w") as file:
        file.write(usersSCSV)


def __generateLocaleConfig(config: Locale):
    address = config.address or config.lang

    lcVars = {
        "ADDRESS": address,
        "IDENTIFICATION": config.identification or address,
        "MEASUREMENT": config.measurement or address,
        "MONETARY": config.monetary or address,
        "NAME": config.name or address,
        "NUMERIC": config.numeric or address,
        "PAPER": config.paper or address,
        "TELEPHONE": config.telephone or address,
        "TIME": config.time or address,
    }

    lcVars = "\n".join(f"LC_{key}={value}" for key, value in lcVars.items())
    localeConf = f"LANG={config.lang}\n{lcVars}"

    with open(path.join(nest_autogen, "locale.conf"), "w") as file:
        file.write(localeConf)

    usedLocales = set(value for value in asdict(config).values() if value)
    requiredLocales = set()

    with open("/etc/locale.gen", "r") as file:
        for locale in file:
            locale = locale.strip().lstrip(" #")

            if any(used in locale for used in usedLocales):
                requiredLocales.add(f"{locale}\n")

    with open(path.join(nest_autogen, "locale.gen"), "w") as file:
        file.writelines(requiredLocales)


def __generateSystemConfig(configDict: dict):
    scsvConfig = ""

    for key in configDict:
        value = __checkValue(key, configDict[key])

        if value == False:
            continue
        if type(value) != str:
            return 4
        scsvConfig += f"{key},{value}\n"

    with open(path.join(nest_autogen, "config.scsv"), "w") as file:
        file.write(scsvConfig)
