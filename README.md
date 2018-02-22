# OMdatabase

Command line tool for prepare database for NGS analysis.
Currently only support [Ensembl](http://asia.ensembl.org/index.html) database.
[![Build Status](https://travis-ci.org/bioShaun/OMdatabase.svg?branch=master)](https://travis-ci.org/bioShaun/OMdatabase)

-----

## Installation

```bash
git clone https://github.com/bioShaun/OMdatabase.git
cd OMdatabase
pip install .

```

## Usage

```
oms_database --help

Usage: oms_database [OPTIONS]

  Command line tool for prepare database for NGS analysis
  
  Options:
	-s, --species TEXT              Species latin name.  [required]
	-d, --database TEXT             Public database name.
	-v, --version TEXT              Database version.
	-a, --analysis TEXT             Analysis for which the database is build for.
	-r, --run [download|build]      Choose to download, build or update
	-l, --launch [local|slurm]      Choose to launch job local or on slurm.
	--help                          Show this message and exit.

Usage Examples:
# Download ensembl annotation for aspergillus nidulans
oms_database -s aspergillus_nidulans -r download

# Download and build database for arabidopsis thaliana
oms_database -s arabidopsis_thaliana -r build
```


