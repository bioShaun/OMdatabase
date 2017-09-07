from ftplib import FTP
from rnaseq.utils import config
from rnaseq.utils import database
import os
import species
# from . import species
import re


HOST_DICT = {
    'animal': 'ftp.ensembl.org',
    'plant': 'ftp.ensemblgenomes.org'}


def save_mkdir(path):
    if not os.path.isdir(path):
        os.makedirs(path)


class PrepareDatabase(object):

    def __init__(self, species, version='current', force=False):
        self.species = species
        self.version = version
        self.force = force
        self.download_fa = True
        self.release = ''
        self.g_version = ''
        self.ftp_genome_dir = ''

    def _prepare(self):
        _species = ' '.join(self.species.split('_'))
        my_sp_inf = species.Species(_species)
        self.kingkom = my_sp_inf.kingdom
        self.host = HOST_DICT[self.kingkom]
        # get database version
        ftp = FTP(self.host)
        ftp.login()
        self.ftp_genome_dir = '/pub/{v}_fasta/{s}/dna'.format(
            s=self.species, v=self.version)
        if self.version == 'current':
            ftp.cwd('/pub/current_fasta/')
            self.release = ftp.pwd().split('/')[-2]
        else:
            self.release = self.version
        self.database_detail = database.sepcies_annotation_path(
            'ensembl', self.species, self.release)
        self.database_detail.get_anno_inf()
        ftp.quit()

    def _get_genome_version(self):
        ftp = FTP(self.host)
        ftp.login()
        ftp.cwd(self.ftp_genome_dir)
        fa_list = ftp.nlst()
        for each_fa in fa_list:
            if 'dna.toplevel.fa.gz' in each_fa:
                genome_fa = each_fa
        g_pattern = re.compile('{s}.(\S+).dna.toplevel.fa.gz'.format(
            s=self.species.capitalize()
        ))
        g_version = g_pattern.match(genome_fa).groups()[0]
        ftp.quit()
        return genome_fa, g_version

    def _download_ensembl(self, f_path, f_name, f_out):
        ftp = FTP(self.host)
        ftp.login()
        ftp.cwd(f_path)
        with open(f_out) as f_out_inf:
            ftp.retrbinary('RETR %s' % f_name, f_out_inf.write)
        ftp.quit()

    def download(self):
        self._prepare()
        if not os.path.exists(self.database_detail.genome_fa):
            genome_fa, self.g_version = self._get_genome_version()
            self.genome_dir = os.path.join(
                config.database['genome'], 'ensembl', self.kingdom,
                self.species, 'genome', self.g_version)
            genome_path = os.path.join(
                self.genome_dir, genome_fa.rstrip('.gz'))
            if not os.path.exists(genome_path):
                save_mkdir(self.genome_dir)
                self._download_ensembl(
                    self.ftp_genome_dir, genome_fa,
                    '{g}.gz'.format(g=genome_path))
        if not os.path.exists(self.database_detail.gtf):
            self.database_dir = os.path.basename(self.database_detail.gtf)
            save_mkdir(self.database_dir)
            ftp_gtf_dir = '/pub/{v}_gtf/{s}/'.format(
                s=self.species, v=self.version)
            gtf_file = '{s}.{g}.{d}.gtf.gz'.format(
                s=self.species.capitalize(), g=self.g_version,
                d=self.release.split('-')[-1])
            self._download_ensembl(ftp_gtf_dir, gtf_file,
                                   os.path.join(self.database_dir, gtf_file))
