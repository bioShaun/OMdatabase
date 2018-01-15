from . import ensembl
# import ensembl


DB_MAP = {
    'ensembl': ensembl.DatabaseInf,
}


class DatabaseInf(object):

    def __init__(self, database, species, version='current'):
        self.database = database
        self.species = species
        self.version = version

    @property
    def download_inf(self):
        my_database = DB_MAP[self.database].get_download_inf(self.species, self.version)
        return my_database
