# docs/main.py

def define_env(env):
    """
    This is the hook function. It's where you can define your macros.
    """
    # This makes the 'pdf' variable available to the templates
    env.variables['pdf'] = env.conf['extra']['pdf']
