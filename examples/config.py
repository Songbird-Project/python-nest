import nest

def preBuild():
    print("Hello, World!")

config = nest.newConfig()

config.preBuild = preBuild

nest.returnConfig(config)
