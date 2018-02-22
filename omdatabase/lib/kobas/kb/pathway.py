#!/usr/bin/env python

from kobas.kb.pid import pid_xml
from kobas.kb.reactome import uniprot_2_pathways
from kobas.kb.panther import sap
from kobas.kb.biocyc import col

def insert_pid(kobasdb, kobasdir):
    pathways, gene_pathways = pid_xml.parse(open(kobasdir + '/pid/NCI-Nature_Curated.xml'), kobasdb)
    kobasdb.con.executemany('INSERT INTO Pathways VALUES (?, ?, ?, ?)', pathways)
    kobasdb.con.executemany('INSERT INTO GenePathways VALUES (?, ?)', gene_pathways)

def insert_reactome(kobasrc, kobasdir):
    uniprot_2_pathways.parse(open(kobasdir + '/reactome/uniprot_2_pathways.stid.txt'), \
        open(kobasdir + '/reactome/curated_and_inferred_uniprot_2_pathways.txt'), \
        kobasrc)

def insert_panther(kobasrc, kobasdir):
    sap.parse(open(kobasdir + '/panther/SequenceAssociationPathway3.3.txt'), kobasrc)

def insert_biocyc(kobasdb, kobasdir, bcdir):
    pathways, gene_pathways = col.parse(open(kobasdir + '/biocyc/' + bcdir + '/genes.col'), \
            open(kobasdir + '/biocyc/' + bcdir + '/pathways.col'), kobasdb)
    kobasdb.con.executemany('INSERT INTO Pathways VALUES (?, ?, ?, ?)', pathways)
    kobasdb.con.executemany('INSERT INTO GenePathways VALUES (?, ?)', gene_pathways)
