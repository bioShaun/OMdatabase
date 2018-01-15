from omdatabase.utils import config
import os


class DatabasePath(object):

    def __init__(self, database, kingdom,
                 species, genome_version,
                 release):
        self.database = database
        self.kingdom = kingdom
        self.species = species
        self.genome_version = genome_version
        self.release = release
        self.genome_dir = None
        self.anno_dir = None
        self.genome_fa = None
        self.genome_gtf = None

    def get_path(self):
        sp_dir = os.path.join(config.BASE_DIR,
                              self.database,
                              self.kingdom,
                              self.species)
        self.genome_dir = os.path.join(sp_dir,
                                       'genome',
                                       self.genome_version)
        self.anno_dir = os.path.join(sp_dir,
                                     'annotation',
                                     self.release)

        def get_annotation_path(x):
            return os.path.join(self.anno_dir,
                                '{0}.{1}'.format(self.species, x))

        self.genome_fa = get_annotation_path('genome.fa')
        self.genome_gtf = get_annotation_path('genome.gtf')

    @classmethod
    def from_dbobj(cls, dbobj):
        db_path = cls(dbobj.database,
                      dbobj.kingdom,
                      dbobj.species,
                      dbobj.genome_version,
                      dbobj.release)
        db_path.get_path()
        return db_path
