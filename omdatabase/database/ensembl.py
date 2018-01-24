from ftplib import FTP
from omdatabase.lib import species
from omdatabase.utils import config
import re
import os

HOST_DICT = {'animal': 'ftp.ensembl.org', 'plant': 'ftp.ensemblgenomes.org'}


def ftp_login(func):
    def wrapper(self):
        self.ftp = FTP(self.host)
        self.ftp.login()
        r = func(self)
        return r
        self.ftp.quit()

    return wrapper


class DatabaseInf(object):
    def __init__(self, species, version='current'):
        self.database = 'ensembl'
        self.species = species
        self.version = version
        self.host = None
        self.ftp = None
        self.kingdom = None
        self.release = None
        self.genome_version = None
        self.genome_url = None
        self.gtf_url = None

    def _get_host(self):
        my_sp_inf = species.Species(self.species)
        self.kingdom = my_sp_inf.kingdom
        self.host = HOST_DICT[self.kingdom]
        return self.host

    @ftp_login
    def _get_release(self):
        if self.version != 'current':
            self.release = self.version
        else:
            # get database version
            if self.kingdom == 'animal':
                self.ftp.cwd('/pub/current_fasta/')
            else:
                self.ftp.cwd('/pub/plants/current/')
            self.release = self.ftp.pwd().split('/')[2]
        return self.release

    def _ftp_prefix(self, data_type):
        if self.kingdom == 'animal':
            return '/pub/{t.release}/{d}/{t.species}/'.format(
                t=self, d=data_type)
        else:
            return '/pub/plants/{t.release}/{d}/{t.species}/'.format(
                t=self, d=data_type)

    @ftp_login
    def _get_genome(self):
        genome_dir = os.path.join(self._ftp_prefix('fasta'), 'dna')
        self.ftp.cwd(genome_dir)
        fa_list = self.ftp.nlst()
        for each_fa in fa_list:
            if 'dna.toplevel.fa.gz' in each_fa:
                genome_fa = each_fa
                break
        g_pattern = re.compile(
            '{s}.(\S+).dna.toplevel.fa.gz'.format(s=self.species.capitalize()))
        self.genome_version = g_pattern.match(genome_fa).groups()[0]
        self.genome_url = os.path.join(genome_dir, genome_fa)
        return self.genome_url, self.genome_version

    def _get_gtf(self):
        gtf_dir = self._ftp_prefix('gtf')
        gtf_file = '{s}.{g}.{d}.gtf.gz'.format(
            s=self.species.capitalize(),
            g=self.genome_version,
            d=self.release.split('-')[-1])
        self.gtf_url = os.path.join(gtf_dir, gtf_file)
        return self.gtf_url

    def _load_db(self):
        self._get_host()
        if self.release is None:
            self._get_release()
        db_release = '{t.database}-{t.release}'.format(t=self)
        if (self.species in config.db_saved
                and db_release in config.db_saved[self.species]):
            self.genome_version = config.db_saved[self.species][db_release][0]
            self.genome_url = config.db_saved[self.species][db_release][1]
            self.gtf_url = config.db_saved[self.species][db_release][2]
        else:
            self._get_genome()
            self._get_gtf()

    @classmethod
    def get_download_inf(cls, species, version):
        my_db_inf = cls(species, version)
        my_db_inf._load_db()
        config.update_db(my_db_inf)
        return my_db_inf
