from .dbt_magics import DBTMagics

def load_ipython_extension(ipython):
    """
    Complete Example
    - https://ipython.readthedocs.io/en/8.17.1/config/custommagics.html#complete-example
    """

    ipython.register_magics(DBTMagics)