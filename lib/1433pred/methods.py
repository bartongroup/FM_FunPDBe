#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import os
import sys
import time
import random
import json
import sqlite3
import tempfile
from datetime import datetime
DEV = "www1433"
# sys.path.append("/homes/www-1433/%s/app/test/lib/python2.6/site-packages/old/" % DEV)

import requests

# PATH = "/homes/www-1433/%s/app/" % DEV
PATH = os.path.dirname(__file__)
# TMP_PATH = "/homes/www-1433/tmp/"
TMP_PATH = tempfile.gettempdir()
DB_PATH = "/homes/www-1433/"


aa_common = ['A', 'C', 'D', 'E', 'F', 'G', 'H',
             'K', 'I', 'L', 'M', 'N', 'P', 'Q',
             'R', 'S', 'T', 'V', 'Y', 'W',
             'B', 'X', 'Z', 'J', 'U', 'O', '-',
             'X', 'B', 'U', '*']


def ctime():
    """
    Gets current time to load into log files.
    """

    date = datetime.now()
    year = date.strftime("%Y")
    month = date.strftime("%m")
    day = date.strftime("%d")
    hour = date.strftime("%H")
    minute = date.strftime("%M")
    second = date.strftime("%S")
    curr_time = "%s/%s/%s %s:%s:%s" % (day, month, year, hour, minute, second)

    return curr_time


def get_random_string_with_n_digits(n):
    """
    Gets a random number with N digits.

    @param n: number of digits
    @return: returns a random integer (int)
    """

    range_start = 10 ** (n - 1)
    range_end = (10 ** n) - 1

    return random.randint(range_start, range_end)


def validate_uniprot(identifier):
    """
    Checks if the inputed UniProt ID is valid.

    @param identifier: UniProt ID
    @return: returns a boolean, a FASTA header, a protein sequence and an accession
        if it manages to get one.
    """

    full_sequence = ""

    try:
        url = 'http://www.uniprot.org/uniprot/%s.fasta' % identifier.upper()
        read = requests.get(url)
        if read.status_code == 200:
            full_sequence = read.text
            valid = True
        else:
            valid = False
    except:
        valid = False

    return valid, full_sequence


def validate_fasta(area):
    """
    Checks if the inputed Sequence is valid.

    @param sequence: FASTA sequence
    @return: returns a boolean, a FASTA header and a protein sequence
    """

    full_sequence = area
    try:
        area = area.lstrip()
        area = area.rstrip()

        if "\n" in area or "\r\n" in area:
            try:
                area = area.split("\r\n")
            except:
                area = area.split("\n")

            if ">" in area[0]:
                valid = True
                for entry in area[1:]:
                    sequence = entry
                    for res in sequence:
                        if res not in aa_common:
                            valid = False
                            break
            else:
                valid = False

        else:
            valid = False

    except:
        valid = False

    return valid, full_sequence


def validate_file(infile):
    """
    Checks if the inputed File is valid. Including extension.
    (and size and FASTA contents)

    @param sequence: Several FASTA sequences
    @return: returns a boolean, an protein sequences

    :param file: Inputed File
    :return: returns a boolean
    """

    # These are the extension that we are accepting to be uploaded
    allowed_extensions = ['txt', 'fasta', 'fa']

    valid = False
    # For a given file, return whether it's an allowed type or not

    if '.' in infile and infile.rsplit('.', 1)[1] in allowed_extensions:
        valid = True

    return valid


def write_features(output_file, header, three, two, one, phospho):
    """
    Writes out a features file for us with JalviewLite.

    @param output_file: output file
    @param header: FASTA header
    @param three: Highly score sites
    @param two: Medium scored sites
    @param one: lowly scored sites
    @param phospho: phosphoSites
    @return: returns a document out
    """

    # create temporary files
    global TMP_PATH

    out = open(os.path.join(TMP_PATH, output_file), "w")
    out.write("""HIGH_CONFIDENCE\tCEEECE
MEDIUM_CONFIDENCE\tC4EAF6
LOW_CONFIDENCE\tFEF6DB
PHOSPHORYLATED\tBB0909

""")

    # three
    out.write("STARTGROUP\tPREDICTOR\n")
    for entry in three:
        out.write("PREDICTOR\t%s\t-1\t%s\t%s\tHIGH_CONFIDENCE\n" % (header, entry, entry))
    out.write("ENDGROUP\tPREDICTOR\n\n")

    # two
    out.write("STARTGROUP\tPREDICTOR\n")
    for entry in two:
        out.write("PREDICTOR\t%s\t-1\t%s\t%s\tMEDIUM_CONFIDENCE\n" % (header, entry, entry))
    out.write("ENDGROUP\tPREDICTOR\n\n")

    # one
    out.write("STARTGROUP\tPREDICTOR\n")
    for entry in one:
        out.write("PREDICTOR\t%s\t-1\t%s\t%s\tLOW_CONFIDENCE\n" % (header, entry, entry))
    out.write("ENDGROUP\tPREDICTOR\n\n")

    # phospho
    out.write("STARTGROUP\tPHOSPHORYLATION\n")
    for entry in phospho:
        out.write("PHOSPHORYLATION\t%s\t-1\t%s\t%s\tPHOSPHORYLATED\n" % (header, entry, entry))
    out.write("ENDGROUP\tPHOSPHORYLATION\n\n")

    out.close()
    return


def get_phosphosites(identifier):
    """
    Gets phosphorylated Sites from UniProt.

    :param identifier: UniProt ID
    :return: returns a list of positions
    """

    phospho_sites = list()

    try:
        # pSer/The from UniProt
        url = 'http://www.uniprot.org/uniprot/%s.txt' % identifier.upper()
        try:
            read = requests.get(url)
        except:
            time.sleep(1)
            read = requests.get(url)

        if read.status_code == 200:
            for line in read.iter_lines():
                # example lines
                """
                FT   MOD_RES      41     41       Phosphoserine.
                FT   MOD_RES     104    104       Phosphoserine.
                FT   MOD_RES     148    148       Phosphoserine.
                FT   MOD_RES     167    167       Phosphoserine.
                FT   MOD_RES     181    181       Phosphoserine.
                FT   MOD_RES     187    187       Phosphothreonine.
                FT   MOD_RES     195    195       Phosphoserine.
                FT   MOD_RES     258    258       Phosphoserine.
                FT   MOD_RES     267    267       Phosphoserine.
                FT   MOD_RES     291    291       Phosphoserine.
                """
                if "FT   MOD_RES" in line:
                    line = line.rstrip("\r\n")
                    if "Phosphoserine" in line or "Phosphothreonine" in line:
                        line = line.split()
                        phospho = line[2]
                        phospho_sites.append(phospho)

        # pSer/The from PhosphoSitePlus
        read = open("PhosphoSite.txt")
        lines = read.readlines()
        for line in lines:
            line = line.rstrip("\r\n")

            uni = line.split("\t")[0]
            site = line.split("\t")[1]
            if uni == identifier:
                phospho_sites.append(site)

    except:
        pass

    return phospho_sites


def get_table_results(job_id):
    """
    Parses the results to get formated results for the website.

    :param job_id: random job id
    :return: returns accession, header, sequence, results
    """

    global TMP_PATH
    accession = ""
    header = ""
    nsequence = ""
    results = []

    # parse the fasta file
    from Bio import SeqIO
    link_fasta = "1433pred_%s.fasta" % job_id
    record = SeqIO.read(os.path.join(TMP_PATH, link_fasta), "fasta")
    sequence = str(record.seq)
    identifier = str(record.id)
    header = str(record.description)
    # e.g. sp|P16188|1A30_HUMAN
    try:
        identifier = identifier.split("|")[1]
    except:
        pass

    accession = identifier
    header = ">" + header
    bsequence = ""
    indexer = 0
    for i in range(0, len(sequence), 60):
        bsequence += sequence[indexer:i] + "\n"
        indexer = i
    bsequence += sequence[indexer:len(sequence)]
    bsequence = bsequence.lstrip()
    nsequence = ""
    for res in bsequence:
        if res == "S" or res == "T":
            nsequence += "<strong><ins>" + res + "</ins></strong>"
        else:
            nsequence += res

    # parse predictions
    link_full = "1433pred_%s.full" % job_id
    with open(os.path.join(TMP_PATH, link_full)) as lines:
        count = 0
        for line in lines:
            count += 1
            if count != 1:
                line = line.strip()
                line = line.split("\t")
                position = line[0]
                peptide = line[1]
                ann = line[2]
                pssm = line[3]
                svm = line[4]
                consensus = line[5]
                candidate = line[6]
                phospho = line[7]
                results.append([position, peptide, ann, pssm, svm, consensus, candidate, phospho])

    link_svg = "1433pred_%s.svg" % job_id
    op = open(os.path.join(TMP_PATH, link_svg))
    full_svg = op.read()
    op.close()

    return accession, header, nsequence, results, full_svg


def check_status(job_id):
    """
    Checks if the files have been created and changes the status to Done.

    :param job_id: random job id
    :return: returns the status of the job
    """

    global TMP_PATH

    status = "Running"
    link_csv = "1433pred_%s.csv" % job_id
    link_tsv = "1433pred_%s.tsv" % job_id
    link_json = "1433pred_%s.json" % job_id
    link_error = "1433pred_%s.log" % job_id
    link_fasta = "1433pred_%s.fa" % job_id
    link_feat = "1433pred_%s.feat" % job_id
    link_svg = "1433pred_%s.svg" % job_id
    full_svg = ""
    log_code = ""
    accession = ""
    header = ""
    sequence = ""
    results = ""

    if os.path.isfile(os.path.join(TMP_PATH, link_error)):
        status = "Error"
        read = open(os.path.join(TMP_PATH, link_error), "r")
        lines = read.readlines()
        read.close()
        for line in lines:
            if "> Error:" in line:
                line = line.rstrip("\r\n")
                log_code = line.lstrip("> Error: ")

    elif os.path.isfile(os.path.join(TMP_PATH, link_csv)) and os.path.isfile(os.path.join(TMP_PATH, link_tsv)) and \
            os.path.isfile(os.path.join(TMP_PATH, link_json)) and os.path.isfile(os.path.join(TMP_PATH, link_fasta)) and \
            os.path.isfile(os.path.join(TMP_PATH, link_feat)) and os.path.isfile(os.path.join(TMP_PATH, link_svg)):
        status = "Complete"

        accession, header, sequence, results, full_svg = get_table_results(job_id)

    return status, accession, header, sequence, results, link_fasta, link_feat, link_csv, link_tsv, \
                link_json, link_svg, full_svg, log_code


def check_status_long(job_id):
    """
    Checks if the files have been created and changes the status to Done.

    :param job_id: random job id
    :return: returns the status of the job
    """

    global TMP_PATH

    status = "Running"
    link_csv = "1433pred_%s.csv" % job_id
    link_tsv = "1433pred_%s.tsv" % job_id
    link_json = "1433pred_%s.json" % job_id
    link_error = "1433pred_%s.log" % job_id
    log_code = ""

    if os.path.isfile(os.path.join(TMP_PATH, link_error)):
        status = "Error"
        read = open(os.path.join(TMP_PATH, link_error), "r")
        lines = read.readlines()
        read.close()
        for line in lines:
            if "> Error:" in line:
                line = line.rstrip("\r\n")
                log_code = line.lstrip("> Error: ")

    elif os.path.isfile(os.path.join(TMP_PATH, link_csv)) and os.path.isfile(os.path.join(TMP_PATH, link_tsv)) and \
            os.path.isfile(os.path.join(TMP_PATH, link_json)):
        status = "Complete"

    return status, link_csv, link_tsv, link_json, log_code


def load_sqlite(identifier, method="ANN", unique=True):
    """
    Generic routine to load information from the SQLITE database.
    """

    global DB_PATH

    # flash("Loading JSON object from SQLite3 Database...")

    # load information from the SQLite3 db
    con = None
    sqlite3.register_converter("json", json.loads)
    local_db = "%s.db" % method
    if unique:
        data = None
    else:
        data = list()

    try:
        con = sqlite3.connect(os.path.join(DB_PATH, local_db),
                              detect_types=sqlite3.PARSE_DECLTYPES or sqlite3.PARSE_COLNAMES)
        with con:
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            # get results from the analysis
            # try to get that entry from the DB
            cur.execute("""SELECT * FROM snapshot""")
            try:
                while True:
                    row = cur.fetchone()
                    if row["Peptide"] == identifier:
                        data = row["Score"]
                        if unique:
                            break
                        else:
                            data.append(row["Score"])
            except:
                raise ValueError("No value in the db.")
                # print("Warning: No value for %s in SQLite..." % identifier)

    except sqlite3.Error as e:
        # print("Warning: Database %s not available... %s" % (method, e.args[0]))
        raise ValueError("No table in DB.")

    finally:
        if con:
            con.close()

    return data


def store_sqlite(identifier, method="ANN", information=None, save=True):
    """
    Generic routine to store information and the analysis results of
    the structures and variation data.
    """

    global DB_PATH

    # flash("Storing JSON object in SQLite3 Database...")

    # save log records of what has been updated and what failed
    # output_file = "log_%s_success.txt" % method
    # outlog1 = open(path + output_file, "a")
    # output_file = "log_%s_error.txt" % method
    # outlog2 = open(path + output_file, "a")

    # load information into the SQLite3 db
    con = None
    sqlite3.register_converter("json", json.loads)
    local_db = "%s.db" % method

    try:
        con = sqlite3.connect(os.path.join(DB_PATH, local_db),
                              detect_types=sqlite3.PARSE_DECLTYPES or sqlite3.PARSE_COLNAMES)
        with con:
            # flash("Connected to .NOBACK/DB/%s.db SQLite3 Database..." % method)
            con.row_factory = sqlite3.Row
            cur = con.cursor()

            try:
                # get results from the analysis
                if save:
                    # write down json file
                    json_string = json.dumps(information, sort_keys=False, indent=4)

                    # try to get that entry from the DB
                    json_id = json.dumps(identifier)
                    try:
                        cur.execute("""SELECT * FROM snapshot""")
                        while True:
                            row = cur.fetchone()
                            if row["Peptide"] == identifier:
                                # update previous entry
                                cur.execute("""UPDATE snapshot SET Score=? WHERE Peptide=?""",
                                            (json_string, json_id))
                                con.commit()
                                # outlog1.write("%s\t%s\n" % (time(), identifier))
                                # flash("Updated JSON object in .NOBACK/DB/%s.db (SQLite3) for ID %s..." % (method, identifier))
                                break
                    except:
                        try:
                            cur.execute("""CREATE TABLE snapshot(Peptide json PRIMARY KEY, Score json)""")
                            con.commit()
                        except:
                            # print("Warning: Table 'snapshot' already exists...")
                            pass
                        try:
                            cur.execute("""INSERT INTO snapshot VALUES(?, ?)""",
                                        (json_id, json_string))
                            con.commit()
                            # outlog1.write("%s\t%s\n" % (time(), identifier))
                            # flash("Stored JSON object in .NOBACK/DB/%s.db (SQLite3) for ID %s..." % (method, identifier))
                        except sqlite3.Error as e:
                            # print("%s\tError: %s\n" % (identifier, e.args[0]))
                            # outlog2.write("%s\t%s\tError: %s\n" % (time(), identifier, e.args[0]))
                            pass
                else:
                    # flash("Skipping saving JSON object in .NOBACK/DB/%s.db (SQLite3) for ID %s..." % (method,
                    #                                                                                   identifier))
                    pass
            except sqlite3.Error as e:
                # print("%s\tError: %s\n" % (identifier, e.args[0]))
                # outlog2.write("%s\t%s\tError: %s\n" % (time(), identifier, e.args[0]))
                pass

    except sqlite3.Error as e:
        # print("%s\tError: %s\n" % (identifier, e.args[0]))
        # outlog2.write("%s\t%s\tError: %s\n" % (time(), identifier, e.args[0]))
        pass

    finally:
        if con:
            con.close()
            # flash("Disconnected from .NOBACK/DB/%s.db SQLite3 Database..." % method)

    # outlog1.close()
    # outlog2.close()
    return


def run():
    """
    Used to create a simple and memory friendly PhosphoSite.txt
    used to parse the pSer/Thr.

    :return: updated PhosphoSite.txt
    """
    out = open("PhosphoSite.txt", "w")

    read = open("Phosphorylation_site_dataset")
    lines = read.readlines()
    read.close()
    for line in lines:
        line = line.rstrip("\r\n")

        try:
            uni = line.split("\t")[1]
            site = line.split("\t")[5]
            if "S" in site or "T" in site:
                site = (line.split("\t")[5]).lstrip("ST")
                out.write("%s\t%s\n" % (uni, site))
        except:
            pass
    out.close()


if __name__ == "__main__":
    # run()
    # read = open("PhosphoSite.txt", "r")
    # lines = read.readlines()
    # read.close()
    # for line in lines:
    #     line = line.rstrip("\r\n")
    #
    #     uni = line.split("\t")[0]
    #     site = line.split("\t")[1]
    #     store_sqlite(uni, method="PhosphoSite", information=site, save=True)
    # sequence = "MFGKRKKRVEISAPSNFEHRVHTGFDQHEQKFTGLPRQWQSLIEESARRPKPLVDPACITSIQPGAPKTIVRGSKGAKDGALTLLLDEFENMSVTRSNSLRRDSPPPPARARQENGMPEEPATTARGGPGKAGSRGRFAGHSEAGGGSGDRRRAGPEKRPKSSREGSGGPQESSRDKRPLSGPDVGTPQPAGLASGAKLAAGRPFNTYPRADTDHPSRGAQGEPHDVAPNGPSAGGLAIPQSSSSSSRPPTRARGAPSPGVLGPHASEPQLAPPACTPAAPAVPGPPGPRSPQREPQRVSHEQFRAALQLVVDPGDPRSYLDNFIKIGEGSTGIVCIATVRSSGKLVAVKKMDLRKQQRRELLFNEVVIMRDYQHENVVEMYNSYLVGDELWVVMEFLEGGALTDIVTHTRMNEEQIAAVCLAVLQALSVLHAQGVIHRDIKSDSILLTHDGRVKLSDFGFCAQVSKEVPRRKSLVGTPYWMAPELISRLPYGPEVDIWSLGIMVIEMVDGEPPYFNEPPLKAMKMIRDNLPPRLKNLHKVSPSLKGFLDRLLVRDPAQRATAAELLKHPFLAKAGPPASIVPLMRQNRTR"
    # header = ""
    # identifier = "O96013"
    # get_table_results(sequence, header, identifier)
    pass