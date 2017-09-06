from ftplib import FTP
from rnaseq.utils import config
from rnaseq.utils import database
import os
from . import species


HOST_DICT = {
    'animal': 'ftp.ensembl.org',
    'plant': 'ftp.ensemblgenomes.org'}


class PrepareDatabase(object):

    def __init__(self, species, version='current', force=False):
        self.species = species
        self.version = version
        self.force = force
        self.is_download = False
        self.release = ''

    def _prepare(self):
        _species = self.species.split('_')
        my_sp_inf = species.Species(_species)
        self.kingkom = my_sp_inf.kingdom()
        self.host = HOST_DICT[self.kingkom]
        self.database_dir = os.path.join(
            config.database['genome'], 'ensembl', self.kingkom, self.species)

    def _check(self):
        # check if database is downloaded
        ftp = FTP(self.host)
        ftp.login()
        if self.version == 'current':
            ftp.cwd('pub/current_fasta/')
            self.release = ftp.pwd().split('/')[-2]
        else:
            self.release = self.version
        my_sp_path = database.sepcies_annotation_path()


    def download(self):
        ftp = FTP(self.host)
        ftp.login()
        ftp.cwd(
            '/pub/{v}_fasta/{s}/dna'.format(s=self.species, v=self.version))
