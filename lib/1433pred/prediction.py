#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import os
import sys
import json

DEV = "www1433"
sys.path.append("/homes/www-1433/%s/app/test/lib/python2.6/site-packages/" % DEV)
sys.path.append("/homes/www-1433/%s/app/test/lib/python2.6/site-packages/old/" % DEV)


def get_prediction_results(arg_input, arg_output, multiple=False):
    """
    Gets every Ser/Thr residue for each inputed protein and scores it using
    ANN, PSSM, SVM and Consensus classifiers.

    @param arg_input: name of the input file (protein sequences in FASTA)
    @param arg_output: name of the output directory
    @param multiple: multiple is True for multiple sequences
    @return: prints out both cvs and tsv result files
    """

    # loading these here so that the program still prints out the
    # script usage

    from Bio import SeqIO
    # from Bio.Alphabet import IUPAC

    from methods import ctime
    # from methods import load_sqlite, store_sqlite

    from predictor import pssm_prediction
    from predictor import ann_prediction
    from predictor import svm_prediction

    # capturing input filename
    try:
        filename = arg_input.split("/")[-1]
        filename = filename.split(".")[0]
    except:
        filename = arg_input

    path = arg_output

    if multiple:
        # going through the sequences
        try:
            lcsv = []
            ltsv = []
            information = []
            count = 0
            read = SeqIO.parse(arg_input, "fasta")
            for record in read:
                sequence = str(record.seq)
                identifier = str(record.id)
                count += 1

                # skip if there is more than 100 sequences
                if count < 100:

                    # e.g. sp|P16188|1A30_HUMAN
                    try:
                        identifier = identifier.split("|")[1]
                    except:
                        pass

                    # test length of sequence
                    if len(sequence) < 30:
                         raise ValueError("Inputed sequence with ID %s was too short (<30 amino acids)." % identifier)

                    # log queried IDs from the public
                    # if identifier != "":
                    #     try:
                    #         counter = load_sqlite(identifier, method="LOG", unique=True)
                    #     except:
                    #         counter = 0
                    #     # add one to the counter
                    #     store_sqlite(identifier, method="LOG", information=int(counter) + 1, save=True)

                    # going through each sequence
                    full_peptides = []
                    peptides = []
                    position = 0
                    for res in sequence:
                        position += 1
                        if res == "S" or res == "T":
                            res = res.lower()
                            site = position - 1

                            lower = site - 6
                            upper = site + 4 + 1
                            lowergap = ""
                            uppergap = ""
                            if lower < 0:
                                lowerdiff = abs(lower)
                                lower = 0
                                lowergap = "-" * lowerdiff
                            if upper > len(sequence):
                                upperdiff = upper - len(sequence)
                                upper = len(sequence)
                                uppergap = "-" * upperdiff

                            bef = "".join((lowergap, sequence[lower:site]))
                            aft = "".join((sequence[site + 1:upper], uppergap))
                            peptide2 = bef + res + aft
                            peptide3 = bef + aft

                            full_peptides.append([position, peptide2, peptide3])
                            peptides.append(peptide3)

                    # score the peptides using the ANN, PSSM and SVM methods
                    ann_scores = ann_prediction(peptides, filename)
                    pssm_scores = pssm_prediction(peptides)
                    svm_scores = svm_prediction(peptides, filename)

                    information2 = []
                    for entry, ann, pssm, svm in zip(full_peptides, ann_scores, pssm_scores, svm_scores):
                        ann = round(float(ann), 3)
                        pssm = round(float(pssm), 3)
                        svm = round(float(svm), 3)
                        consensus = round((ann + pssm + svm) * 1.0 / 3, 3)
                        position = entry[0]
                        peptide2 = entry[1]

                        # print out the scores
                        lcsv.append("%s,%s,%s,%s,%s,%s,%s,%s\n" % (count, identifier, position, peptide2, ann, pssm, svm, consensus))
                        ltsv.append("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (count, identifier, position, peptide2, ann, pssm, svm, consensus))

                        dictionary = {}
                        dictionary["Identifier"] = identifier
                        dictionary["Site"] = position
                        dictionary["Peptide"] = peptide2
                        dictionary["ANN"] = '{0:.3f}'.format(float(ann))
                        dictionary["PSSM"] = '{0:.3f}'.format(float(pssm))
                        dictionary["SVM"] = '{0:.3f}'.format(float(svm))
                        dictionary["Consensus"] = '{0:.3f}'.format(float(consensus))
                        information2.append(dictionary)

                    information.append(information2)

            if count == 0:
                raise ValueError("No sequences in FASTA format were provided.")

            # create oupput files
            csv = "%s.csv" % filename
            tsv = "%s.tsv" % filename
            js = "%s.json" % filename
            print(os.path.join(path, csv))
            icsv = open(os.path.join(path, csv), "a")
            itsv = open(os.path.join(path, tsv), "a")
            ijson = open(os.path.join(path, js), "w")
            icsv.write("Sequence,Identifier,Site,Peptide_[-6:4],ANN,PSSM,SVM,Consensus\n")
            itsv.write("Sequence\tIdentifier\tSite\tPeptide_[-6:4]\tANN\tPSSM\tSVM\tconsensus\n")

            # go trough files
            for entry in lcsv:
                icsv.write(entry)

            for entry in ltsv:
                itsv.write(entry)

            json_lines = json.dumps(information, sort_keys=False)
            ijson.write(json_lines)

            icsv.close()
            itsv.close()
            ijson.close()

        except Exception as e:
            path = arg_output
            print(os.path.join(path, "%s.log" % filename))
            log = open(os.path.join(path, "%s.log" % filename), "w")
            log.write(
"""Logged error for file '%s' (%s)

> Error: %s

""" % (arg_input, ctime(), e))
            log.close()

    else:
        try:
            record = SeqIO.read(arg_input, "fasta")
            sequence = str(record.seq)
            identifier = str(record.id)
            # e.g. sp|P16188|1A30_HUMAN
            try:
                identifier = identifier.split("|")[1]
            except:
                pass

            # test length of sequence
            if len(sequence) < 30:
                 raise ValueError("Inputed sequence with ID %s was too short (<30 amino acids)." % identifier)

            # log queried IDs from the public
            # if identifier != "":
            #     try:
            #         counter = load_sqlite(identifier, method="LOG", unique=True)
            #     except:
            #         counter = 0
            #     # add one to the counter
            #     store_sqlite(identifier, method="LOG", information=int(counter) + 1, save=True)

            # going through the sequence
            full_peptides = []
            peptides = []
            position = 0
            for res in sequence:
                position += 1

                if res == "S" or res == "T":
                    res1 = "[" + res + "]"
                    res2 = res.lower()
                    site = position - 1

                    lower = site - 6
                    upper = site + 4 + 1
                    lowergap = ""
                    uppergap = ""
                    if lower < 0:
                        lowerdiff = abs(lower)
                        lower = 0
                        lowergap = "-" * lowerdiff
                    if upper > len(sequence):
                        upperdiff = upper - len(sequence)
                        upper = len(sequence)
                        uppergap = "-" * upperdiff

                    bef = "".join((lowergap, sequence[lower:site]))
                    aft = "".join((sequence[site + 1:upper], uppergap))
                    peptide = bef + res1 + aft
                    peptide2 = bef + res2 + aft
                    peptide3 = bef + aft

                    full_peptides.append([position, peptide, peptide2, peptide3])
                    peptides.append(peptide3)

            # score the peptides using the ANN, PSSM and SVM methods
            ann_scores = ann_prediction(peptides, filename)
            pssm_scores = pssm_prediction(peptides)
            svm_scores = svm_prediction(peptides, filename)

            # try:
            #     phospho_sites = load_sqlite(identifier, method="PhosphoSite", unique=False)
            # except:
            from methods import get_phosphosites
            phospho_sites = get_phosphosites(identifier)

            link_csv = "%s.csv" % filename
            link_tsv = "%s.tsv" % filename
            link_json = "%s.json" % filename
            link_full = "%s.full" % filename

            csv = open(os.path.join(path, link_csv), "w")
            csv.write("Site,Peptide_[-6:4],ANN,PSSM,SVM,Consensus,pSer/Thr\r\n")
            tsv = open(os.path.join(path, link_tsv), "w")
            tsv.write("Site\tPeptide_[-6:4]\tANN\tPSSM\tSVM\tconsensus,pSer/Thr\r\n")
            js = open(os.path.join(path, link_json), "w")
            full = open(os.path.join(path, link_full), "w")

            rows = []
            feat_three = []
            feat_two = []
            feat_one = []
            feat_phospho = []
            information = []
            count = 0
            for entry, ann, pssm, svm in zip(full_peptides, ann_scores, pssm_scores, svm_scores):
                count += 1
                consensus = round((float(ann) + float(pssm) + float(svm)) * 1.0 / 3, 3)
                ann = round(float(ann), 3)
                pssm = round(float(pssm), 3)
                svm = round(float(svm), 3)
                position = entry[0]
                peptide = entry[1]
                peptide2 = entry[2]
                if str(position) in phospho_sites:
                    phospho = "Yes"
                    feat_phospho.append(position)
                else:
                    phospho = "-"

                # print out the scores
                csv.write("%s,%s,%s,%s,%s,%s,%s\r\n" % (position, peptide2, ann, pssm, svm, consensus, phospho))
                tsv.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\r\n" % (position, peptide2, ann, pssm, svm, consensus, phospho))
                dictionary = {}
                dictionary["Site"] = position
                dictionary["Peptide"] = peptide2
                dictionary["ANN"] = '{0:.3f}'.format(float(ann))
                dictionary["PSSM"] = '{0:.3f}'.format(float(pssm))
                dictionary["SVM"] = '{0:.3f}'.format(float(svm))
                dictionary["Consensus"] = '{0:.3f}'.format(float(consensus))
                dictionary["pSer/Thr"] = phospho
                information.append(dictionary)

                # get conditional labels
                if ann > 0.55 and pssm > 0.80 and svm > 0.25:
                    candidate = "Three"
                    feat_three.append(position)
                elif (ann > 0.55 and pssm > 0.80) or (ann > 0.55 and svm > 0.25) or (svm > 0.25 and pssm > 0.80):
                    candidate = "Two"
                    feat_two.append(position)
                elif ann > 0.55 or pssm > 0.80 or svm > 0.25:
                    candidate = "One"
                    feat_one.append(position)
                else:
                    candidate = "False"

                # cosmetics in the table view
                consensus = '{0:.3f}'.format(float((float(ann) + float(pssm) + float(svm)) * 1.0 / 3))
                ann = '{0:.3f}'.format(float(ann))
                pssm = '{0:.3f}'.format(float(pssm))
                svm = '{0:.3f}'.format(float(svm))

                if "-" not in ann:
                    ann = "&nbsp;%s" % ann

                if "-" not in pssm:
                    pssm = "&nbsp;%s" % pssm

                if "-" not in svm:
                    svm = "&nbsp;%s" % svm

                if "-" not in consensus:
                    consensus = "&nbsp;%s" % consensus

                rows.append([position, peptide, ann, pssm, svm, consensus, candidate, phospho])
                full.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\r\n" % (position, peptide, ann, pssm, svm, consensus, candidate, phospho))

            json_lines = json.dumps(information, sort_keys=False)
            js.write(json_lines)
            csv.close()
            tsv.close()
            js.close()
            full.close()

            # jaliew-lite
            # import shutil
            # shutil.copyfile(os.path.join(PATH, "static", "jalviewApplet.jar")), os.path.join(TMP_PATH, "jalviewApplet.jar"))
            # shutil.copyfile(os.path.join(PATH, "static", "JmolApplet.jar"), os.path.join(TMP_PATH, "JmolApplet.jar"))
            # fasta for jalview
            fasta = "%s.fa" % filename
            op = open(os.path.join(path, fasta), 'w')
            op.write(">%s\n%s" % (identifier, sequence))
            op.close()

            # features and SVG
            feature = "%s.feat" % filename
            link_svg = "%s.svg" % filename

            # generate the features file for Jalview-
            from methods import write_features
            write_features(feature, identifier, feat_three, feat_two, feat_one, feat_phospho)

            # # generate jalview svg
            # java = "/sw/java/latest/bin/java"
            # jalview = "/cluster/gjb_lab/webservices/www-jpred/devel/JALVIEW"
            # jalview_jar = "/cluster/gjb_lab/webservices/www-jpred/devel/JALVIEW/jalview.jar"
            # jalview_props = "/cluster/gjb_lab/webservices/www-jpred/devel/JALVIEW/jvprops_noannots"
            # cmd = "%s -Djava.ext.dirs=%s -jar %s -headless -props -%s -open %s -annotations %s -svg %s" \
            #       % (java, jalview, jalview_jar, jalview_props, os.path.join(path, fasta), os.path.join(path, feature), os.path.join(path, link_svg))
            # os.system(cmd)
            #
            # if os.path.isfile(os.path.join(path, link_svg)):
            #     dummy = '<text x="2" y="8" style="fill: rgb(0,0,0); fill-opacity: 1.0; font-family: sans-serif; font-size: 10px; " >Right click</text></g><g transform="matrix(1,0,0,1,-3,32)"><text x="2" y="18" style="fill: rgb(0,0,0); fill-opacity: 1.0; font-family: sans-serif; font-size: 10px; " >to add annotation</text>'
            #     op = open(os.path.join(path, link_svg), "r")
            #     lines = op.readlines()
            #     op.close()
            #     op = open(os.path.join(path, link_svg), "w")
            #     nlink_svg = ""
            #     for line in lines:
            #         op.write(line.replace(dummy, ""))
            #         nlink_svg += line.replace(dummy, "") + " \n"
            #     op.close()
            #     # else:
            #     #     nlink_svg = "
            # else:
            #     raise ValueError("SVG failed to generate.")

        except Exception as e:
            log = open(os.path.join(path, "%s.log" % filename), "w")
            log.write(
"""Logged error for file '%s' (%s)

> Error: %s

""" % (arg_input, ctime(), e))
            log.close()

    return


def main():
    """
    Main option parser.

    > Uses Biopython (Python module) sequence parsers and expects
    sequences in FASTA format.

    > To classify peptides using the SVM model the external PyML
    python model is necessary.

    > To classify peptides using the ANN model a local version of the
    compiled C executable is necessary ("./ANN") and hopefully this
    will run in UNIX based systems (only tested in CentOS)

    > No tests have been explicitly made to test whether the previous
    modules are available, so exception errors are expected if those
    are not available.

    """

    import argparse
    parser = argparse.ArgumentParser(description='Calls methods to predict 14-3-3-binding sites.')

    parser.add_argument('-i', dest='input', type=str,
                        help='input sequence file',)
    parser.add_argument('-o', dest='output', type=str,
                        help='output path')
    parser.add_argument('-m', dest='multiple', default=False,
                        help='boolean', action='store_true')

    args = parser.parse_args()

    if isinstance(args.input, str):
        get_prediction_results(args.input, args.output, multiple=args.multiple)

    else:
        print("...No input provided! Check the program help with 'python prediction.py -h'")

    return


if __name__ == "__main__":
    main()
