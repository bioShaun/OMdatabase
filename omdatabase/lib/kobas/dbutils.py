#!/usr/bin/env python

import sys

import sqlite3

P = {'K': 'KEGG PATHWAY', 'n': 'PID', 'b': 'BioCarta', 'R': 'Reactome', 'B': 'BioCyc', 'p': 'PANTHER'}
#     1                    2           3                4                5              6
D = {'o': 'OMIM', 'k': 'KEGG DISEASE', 'f': 'FunDO', 'g': 'GAD', 'N': 'NHGRI GWAS Catalog'}
#     1            2                    3             4           5
G = {'G': 'Gene Ontology'}

class KOBASDB:
    def __init__(self, dbfile):
        self.con = sqlite3.connect(dbfile)
        self.con.isolation_level = None
        self.con.text_factory = str
        self.con.row_factory = sqlite3.Row

##organism
    def organisms(self, name = False):
        if name:
            return self.con.execute('SELECT abbr, name FROM Organisms')
        else:
            return self.con.execute('SELECT abbr FROM Organisms')

    def name_from_abbr(self, abbr):
        return self.con.execute('SELECT name FROM Organisms WHERE abbr = ?', (abbr, )).fetchone()[0]

##ko
    def kos(self, name = False):
        if name:
            return self.con.execute('SELECT koid, name FROM Kos')
        else:
            return self.con.execute('SELECT koid FROM Kos')

    def name_from_koid(self, koid):
        return self.con.execute('SELECT name FROM Kos WHERE koid = ?', (koid, )).fetchone()[0]

    ##redundant SQL sentences in koids_from_gid, koids_from_entrez_gene_id, koids_from_gi, koids_from_uniprotkb_ac, and koids_from_ensembl_gene_id are for dealing with mistakes in KEGG raw data files
    def koids_from_gid(self, gid):
        try:
	    result=self.con.execute('SELECT Kos.koid FROM Kos, KoGenes WHERE KoGenes.gid = ? AND KoGenes.koid = Kos.koid', (gid, ))
	except TypeError:
	    sys.exit('Error message:\nBad blastout format. You can choose to input the FASTA file directly (-t fasta:nuc or fasta:pro) or run blast+ locally against FASTA sequence file in the latest backend databases of KOBAS 2.0. Please refer to instructions(http://kobas.cbi.pku.edu.cn/download.do) for details')
	return result

    def koids_from_entrez_gene_id(self, query):
        return self.con.execute('SELECT Kos.koid FROM Kos, KoEntrezGeneIds WHERE KoEntrezGeneIds.entrez_gene_id = ? AND KoEntrezGeneIds.koid = Kos.koid', (query, ))

    def koids_from_gi(self, query):
        return self.con.execute('SELECT Kos.koid FROM Kos, KoGis WHERE KoGis.gi = ? AND KoGis.koid = Kos.koid', (query, ))

    def koids_from_uniprotkb_ac(self, query):
        return self.con.execute('SELECT Kos.koid FROM Kos, KoUniprotkbAcs WHERE KoUniprotkbAcs.uniprotkb_ac = ? AND KoUniprotkbAcs.koid = Kos.koid', (query, ))

    def koids_from_ensembl_gene_id(self, query):
        return self.con.execute('SELECT Kos.koid FROM Kos, KoEnsemblGeneIds WHERE KoEnsemblGeneIds.ensembl_gene_id = ? AND KoEnsemblGeneIds.koid = Kos.koid', (query, ))

    def koids_from_dblink_id(self, dblink_id, dbtype):
        if dbtype == 'entrez_gene_id':
            return self.koids_from_entrez_gene_id(dblink_id)
        elif dbtype == 'gi':
            return self.koids_from_gi(dblink_id)
        elif dbtype == 'uniprotkb_ac':
            return self.koids_from_uniprotkb_ac(dblink_id)
        elif dbtype == 'ensembl_gene_id':
            return self.koids_from_ensembl_gene_id(dblink_id)

    def pathways_from_koid(self, koid):
        return self.con.execute('SELECT Pathways.pid, Pathways.name FROM KoPathways, Pathways WHERE KoPathways.koid = ? AND KoPathways.pid = Pathways.pid', (koid, ))

    def gidnum_from_koid(self, koid, abbr):
        return self.con.execute('SELECT count(*) FROM KoGenes WHERE koid = ? AND gid LIKE ?', (koid, abbr + ':%')).fetchone()[0]

    def gids_from_koid(self, koid, abbr):
        return self.con.execute('SELECT gid FROM KoGenes WHERE koid = ? AND gid LIKE ?', (koid, abbr + ':%'))

##gene
    def databases_from_abbr(self, abbr):
        if abbr == 'ko':
            return [('K', 'KEGG PATHWAY')]
        elif abbr == 'hsa':
            return P.items() + D.items() + G.items()
        else:
            databases = [(database[0], P[database[0]]) for database in self.con.execute('SELECT DISTINCT db FROM Pathways')]
            count = self.con.execute('SELECT COUNT(*) FROM Gos').fetchone()[0]
            if count:
                databases += G.items()
            return databases

    def genes(self, name = False):
        if name:
            return self.con.execute('SELECT gid, name FROM Genes')
        else:
            return self.con.execute('SELECT gid FROM Genes')

    def allkopathways(self):
        return self.con.execute("SELECT * FROM Pathways")

    def allpathways(self, db):
        return self.con.execute("SELECT pid, id, name FROM Pathways WHERE db = :db", (db, ))

    def alldiseases(self, db):
        return self.con.execute("SELECT did, id, name FROM Diseases WHERE db = :db", (db, ))

    def allgoterms(self):
        return self.con.execute("SELECT goid, name FROM Gos")

    def kopathwaygenenums(self, pid, abbr):
        return self.con.execute('SELECT count(*) FROM GenePathways WHERE pid = ? and gid like ?', (pid, abbr + ':%')).fetchone()[0]

    def pathwaygenenums(self, pid):
        return self.con.execute('SELECT count(*) FROM GenePathways WHERE pid = ?', (pid, )).fetchone()[0]

    def diseasegenenums(self, did):
        return self.con.execute('SELECT count(*) FROM GeneDiseases WHERE did = ?', (did, )).fetchone()[0]
   
    def gogenenums(self, goid):
        return self.con.execute('SELECT count(*) FROM GeneGos WHERE goid = ?', (goid, )).fetchone()[0]

    def name_from_gid(self, gid):
        try:
            result=self.con.execute('SELECT name FROM Genes WHERE gid = ?', (gid, )).fetchone()[0]
        except TypeError:
	    sys.exit('Error message:\nBad blastout format. You can choose to input the FASTA file directly (-t fasta:nuc or fasta:pro) or run blast+ locally against FASTA sequence file in the latest backend databases of KOBAS 2.0. Please refer to instructions(http://kobas.cbi.pku.edu.cn/download.do) for details')
        return result

    def gids_from_entrez_gene_id(self, query):
        return self.con.execute('SELECT gid FROM GeneEntrezGeneIds WHERE entrez_gene_id = ?', (query, ))

    def gids_from_gi(self, query):
        return self.con.execute('SELECT gid FROM GeneGis WHERE gi = ?', (query, ))

    def gids_from_uniprotkb_ac(self, query):
        return self.con.execute('SELECT gid FROM GeneUniprotkbAcs WHERE uniprotkb_ac = ?', (query, ))

    def gids_from_ensembl_gene_id(self, query):
        return self.con.execute('SELECT gid FROM GeneEnsemblGeneIds WHERE ensembl_gene_id = ?', (query, ))

    def gids_from_dblink_id(self, dblink_id, dbtype):
        if dbtype == 'entrez_gene_id':
            return self.gids_from_entrez_gene_id(dblink_id)
        elif dbtype == 'gi':
            return self.gids_from_gi(dblink_id)
        elif dbtype == 'uniprotkb_ac':
            return self.gids_from_uniprotkb_ac(dblink_id)
        elif dbtype == 'ensembl_gene_id':
            return self.gids_from_ensembl_gene_id(dblink_id)

    def entrez_gene_ids_from_gid(self, query):
        return self.con.execute('SELECT entrez_gene_id FROM GeneEntrezGeneIds WHERE gid = ?', (query, ))

    def gis_from_gid(self, query):
        return self.con.execute('SELECT gi FROM GeneGis WHERE gid = ?', (query, ))

    def uniprotkb_acs_from_gid(self, query):
        return self.con.execute('SELECT uniprotkb_ac FROM GeneUniprotkbAcs WHERE gid = ?', (query, ))

    def ensembl_gene_ids_from_gid(self, query):
        return self.con.execute('SELECT ensembl_gene_id FROM GeneEnsemblGeneIds WHERE gid = ?', (query, ))

    def dblink_ids_from_gid(self, gid, dbtype):
        if dbtype == 'entrez_gene_id':
            return self.entrez_gene_ids_from_gid(gid)
        elif dbtype == 'gi':
            return self.gis_from_gid(gid)
        elif dbtype == 'uniprotkb_ac':
            return self.uniprotkb_acs_from_gid(gid)
        elif dbtype == 'ensembl_gene_id':
            return self.ensembl_gene_ids_from_gid(gid)

    def pathways_from_gid(self, gid, db = None):
        if db:
            return self.con.execute('SELECT Pathways.id, Pathways.name FROM GenePathways, Pathways WHERE GenePathways.gid = ? AND GenePathways.pid = Pathways.pid AND Pathways.db = ?', (gid, db))
        else:
            return self.con.execute('SELECT Pathways.db, Pathways.id, Pathways.name FROM GenePathways, Pathways WHERE GenePathways.gid = ? AND GenePathways.pid = Pathways.pid', (gid, ))

    def diseases_from_gid(self, gid, db = None):
        if db:
            return self.con.execute('SELECT Diseases.id, Diseases.name FROM GeneDiseases, Diseases WHERE GeneDiseases.gid = ? AND GeneDiseases.did = Diseases.did AND Diseases.db = ?', (gid, db))
        else:
            return self.con.execute('SELECT Diseases.db, Diseases.id, Diseases.name FROM GeneDiseases, Diseases WHERE GeneDiseases.gid = ? AND GeneDiseases.did = Diseases.did', (gid, ))

    def gos_from_gid(self, gid):
        return self.con.execute('SELECT Gos.goid, Gos.name FROM GeneGos, Gos WHERE GeneGos.gid = ? AND GeneGos.goid = Gos.goid', (gid, ))

    def is_ortholog(self, species_id, ospecies_id):
        return self.con.execute('SELECT COUNT(*) FROM Orthologs WHERE gid = ? AND oid = ?', (species_id, ospecies_id)).fetchone()[0]

    def orthologs_from_abbr(self):
        temp = self.con.execute('SELECT oid FROM Orthologs').fetchall()
        if not temp:
            return None
        else:
            return set(map(lambda ids:ids[0].split(':')[0], temp))
