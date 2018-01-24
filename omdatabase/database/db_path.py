from omdatabase.utils import config
import os
import kobas.config as kobas_config


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
        self.gene2tr = get_annotation_path('gene_trans_map.txt')
        self.ensembl_sp = '{p}{s}'.format(p=self.species[0],
                                          s=self.species.split('_')[1])
        # go file path
        self.go = get_annotation_path('go.txt')
        self.topgo = get_annotation_path('go_gene_go.txt')
        self.go_detail = get_annotation_path('go_detail.txt')
        self.go_anno = get_annotation_path('go_anno.txt')
        self.gene_len = get_annotation_path('gene_length.txt')
        # KEGG file path
        kobasrc = kobas_config.getrc()
        self.ko_pep_dir = kobasrc['blastdb']
        self.ko_db_dir = kobasrc['kobasdb']
        self.kegg_abbr = config.kegg_map[self.species]
        self.kegg_blast = get_annotation_path('gene.kegg.blasttab')

    @classmethod
    def from_dbobj(cls, dbobj):
        db_path = cls(dbobj.database,
                      dbobj.kingdom,
                      dbobj.species,
                      dbobj.genome_version,
                      dbobj.release)
        db_path.get_path()
        return db_path
