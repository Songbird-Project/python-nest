from dataclasses import asdict, dataclass, field
from inspect import getsource
import inspect
from os import getenv, path
from types import FunctionType
from typing import List, Optional
from pathlib import Path
import ast

@dataclass
class LocaleGeneral:
    lang: str = "en_US.UTF-8"
    language: str = lang

@dataclass
class LocaleTime:
    abday: str = "Sun;Mon;Tue;Wed;Thu;Fri;Sat"

@dataclass
class Locale:
    localeGeneral: LocaleGeneral
    localeTime: LocaleTime

@dataclass
class User:
    homeDir: str = ""
    fullName: str = ""
    userName: str = ""
    manageHome: bool = False
    groups: List[str] = field(default_factory=list)

@dataclass
class SystemConfig:
    hostname: str
    kernels: List[str] = field(default_factory=list)
    users: List[User] = field(default_factory=list)
    bootloader: str = "limine"
    initramfsGenerator: str = "booster"
    preBuild: Optional[FunctionType] = None
    postBuild: Optional[FunctionType] = None

os_info = {}
nest_gen_root = getenv("NEST_GEN_ROOT") or ""
nest_autogen = nest_gen_root + "autogen/" if nest_gen_root else ""

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
    usersConfig = config.users
    configDict = asdict(config)
    scsvConfig = ""

    for key in configDict:
        if key == "users":
            value = __checkValue(key, usersConfig)
        else:
            value = __checkValue(key, configDict[key])

        if value == False:
            continue
        if type(value) != str:
            return 4
        scsvConfig += f"{key},{value}\n"

    print(scsvConfig)

def __checkValue(key: str, value):
    if key == "hostname":
        return str(value).replace(" ", "-").lower()
    elif key == "preBuild" or key == "postBuild":
        if value != None:
            buildFunc = [getsource(value), value.__name__]
            __generateBuildFiles(buildFunc, key, value)

        return False
    elif isinstance(value, list):
        if key == "kernels":
            return str.join(",", value)
        elif key == "users":
            __generateUserConfig(value)
            return False
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
            elif (
                    isinstance(node.func, ast.Attribute)
                    and isinstance(node.func.value, ast.Name)
                ):
                    usedModules.add(node.func.value.id)
        if isinstance(node, ast.Name):
            usedModules.add(node.id)
        elif (
                isinstance(node, ast.Attribute)
                and isinstance(node.value, ast.Name)
            ):
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
                        imports.add(f"from {moduleName} import {str.join(",", usedImports)}")
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

    return {
        "imports": imports,
        "functions": localFunctions
    }


def __generateBuildFiles(buildFunc: list[str], buildType: str, funcObject: FunctionType):
    module = __getDependencies(funcObject)
    deps = module["imports"]
    functions = module["functions"]

    if not path.exists(nest_autogen) and nest_autogen != "":
        Path(nest_autogen).mkdir(parents=True)

    with open(f"{nest_autogen}{buildType}.py", "w") as file:
        if deps:
            for dep in sorted(deps):
                file.write(f"{dep}\n")

            file.write("\n")

        if functions:
            for _, func in functions.items():
                file.write(func)

            file.write("\n")

        file.write(buildFunc[0])
        file.write("\n")
        file.write(f"{buildFunc[1]}()")

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
,groups,{str.join(",", user.groups)}

"""

    if not path.exists(nest_autogen) and nest_autogen != "":
        Path(nest_autogen).mkdir(parents=True)

    with open(f"{nest_autogen}users.scsv", "w") as file:
        file.write(usersSCSV)
