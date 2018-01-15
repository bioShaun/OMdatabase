from ftplib import FTP
from omdatabase.lib import species
import re
import os


HOST_DICT = {
    'animal': 'ftp.ensembl.org',
    'plant': 'ftp.ensemblgenomes.org'}


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
            return self.version
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
        g_pattern = re.compile('{s}.(\S+).dna.toplevel.fa.gz'.format(
            s=self.species.capitalize()
        ))
        self.genome_version = g_pattern.match(genome_fa).groups()[0]
        self.genome_url = os.path.join(genome_dir, genome_fa)
        return self.genome_url, self.genome_version

    def _get_gtf(self):
        gtf_dir = self._ftp_prefix('gtf')
        gtf_file = '{s}.{g}.{d}.gtf.gz'.format(
            s=self.species.capitalize(), g=self.genome_version,
            d=self.release.split('-')[-1])
        self.gtf_url = os.path.join(gtf_dir, gtf_file)
        return self.gtf_url

    @classmethod
    def get_download_inf(cls, species, version):
        my_db_inf = cls(species, version)
        my_db_inf._get_host()
        my_db_inf._get_release()
        my_db_inf._get_genome()
        my_db_inf._get_gtf()
        return my_db_inf

    # def _download_ensembl(self, f_path, f_name, f_out):
    #     ftp = FTP(self.host)
    #     ftp.login()
    #     ftp.cwd(f_path)
    #     with open(f_out, 'w') as f_out_inf:
    #         ftp.retrbinary('RETR %s' % f_name, f_out_inf.write)
    #     ftp.quit()

    # def _decompression(self, f_path):
    #     cmd = 'gunzip -c {f}.gz > {f}'.format(f=f_path)
    #     cmd_log = subprocess.Popen(cmd, shell=True)
    #     os.waitpid(cmd_log.pid, 0)
    #     return cmd_log.stderr

    # def download(self):
    #     self._prepare()
    #     genome_fa, self.g_version = self._get_genome_version()
    #     if not os.path.exists(self.database_detail.genome_fa):
    #         genome_fa, self.g_version = self._get_genome_version()
    #         self.genome_dir = os.path.join(
    #             config.database['genome'], 'ensembl', self.kingdom,
    #             self.species, 'genome', self.g_version)
    #         genome_path = os.path.join(
    #             self.genome_dir, genome_fa.rstrip('.gz'))
    #         if not os.path.exists(genome_path):
    #             save_mkdir(self.genome_dir)
    #             self._download_ensembl(
    #                 self.ftp_genome_dir, genome_fa,
    #                 '{g}.gz'.format(g=genome_path))
    #             self._decompression(genome_path)
    #             save_link(genome_path, self.database_detail.genome_fa)
    #     if not os.path.exists(self.database_detail.gtf):
    #         self.database_dir = os.path.dirname(self.database_detail.gtf)
    #         save_mkdir(self.database_dir)
    #         ftp_gtf_dir = '/pub/{v}_gtf/{s}/'.format(
    #             s=self.species, v=self.version)
    #         gtf_file = '{s}.{g}.{d}.gtf.gz'.format(
    #             s=self.species.capitalize(), g=self.g_version,
    #             d=self.release.split('-')[-1])
    #         download_gtf = os.path.join(self.database_dir, gtf_file)
    #         self._download_ensembl(ftp_gtf_dir, gtf_file, download_gtf)
    #         self._decompression(download_gtf.rstrip('.gz'))
    #         save_link(download_gtf.rstrip('.gz'), self.database_detail.gtf)
