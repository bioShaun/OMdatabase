import os
import sys
from ftplib import FTP
import subprocess


def save_mkdir(path):
    if not os.path.isdir(path):
        os.makedirs(path)


def save_link(path, dest):
    path = os.path.abspath(path)
    dest_path = os.path.dirname(dest)
    if not os.path.isdir(dest_path):
        sys.exit('destination directory [{d}] not exists.'.format(d=dest_path))
    if os.path.isfile(path):
        try:
            os.symlink(path, dest)
        except OSError:
            print 'destination file exists.'
    else:
        sys.exit('file [{d}] not exists.'.format(d=path))


def download_ftp(host, f_path, f_out):
    ftp = FTP(host)
    ftp.login()
    with open(f_out, 'wb') as f_out_inf:
        ftp.retrbinary('RETR %s' % f_path, f_out_inf.write)
    ftp.quit()


def decompression(gz_file, out_file):
    cmd = 'gunzip -c {gz} > {ungz}'.format(gz=gz_file,
                                           ungz=out_file)
    r = subprocess.Popen(cmd, shell=True)
    r.communicate()
    return r.stderr


class DownloadDB(object):

    def __init__(self, db_obj, dbpath_obj):
        self.db_obj = db_obj
        self.dbpath_obj = dbpath_obj
        self.download_genome = True
        self.download_gtf = True

    def _check_db(self):
        if os.path.isfile(self.dbpath_obj.genome_fa):
            self.download_genome = False
        else:
            save_mkdir(self.dbpath_obj.genome_dir)
        if os.path.isfile(self.dbpath_obj.genome_gtf):
            self.download_gtf = False
        else:
            save_mkdir(self.dbpath_obj.anno_dir)

    def _download_gtf(self):
        if self.download_gtf:
            gtf_download = os.path.join(self.dbpath_obj.anno_dir,
                                        os.path.basename(self.db_obj.gtf_url))
            download_ftp(self.db_obj.host,
                         self.db_obj.gtf_url,
                         gtf_download)
            decompression(gtf_download, self.dbpath_obj.genome_gtf)
        else:
            print 'gtf file exists!'

    def _download_genome(self):
        if self.download_genome:
            genome_download = os.path.join(
                self.dbpath_obj.genome_dir,
                os.path.basename(self.db_obj.genome_url))
            ungz_genome = genome_download.rstrip('.gz')
            if os.path.isfile(ungz_genome):
                save_link(ungz_genome, self.dbpath_obj.genome_fa)
            else:
                download_ftp(self.db_obj.host,
                             self.db_obj.genome_url,
                             genome_download)
                decompression(genome_download, ungz_genome)
                save_link(ungz_genome, self.dbpath_obj.genome_fa)
        else:
            print 'genome fasta file exists!'

    @property
    def download(self):
        self._check_db()
        self._download_gtf()
        self._download_genome()
