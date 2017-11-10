#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import os
import sys
import tempfile

from Bio import AlignIO
from PyML import SequenceData, SVM
from PyML.classifiers.svm import loadSVM

DEV = "www1433"
# PATH = "/homes/www-1433/%s/app/" % DEV
PATH = os.path.dirname(__file__)
# TMP_PATH = "/homes/www-1433/tmp/"
TMP_PATH = tempfile.gettempdir()

aa_valid = ["A", "R", "N", "D", "C", "Q", "E", "G", "H", "I",
            "L", "K", "M", "F", "P", "S", "T", "W", "Y", "V"]
aa_valid_gap = ["A", "R", "N", "D", "C", "Q", "E", "G", "H", "I",
                "L", "K", "M", "F", "P", "S", "T", "W", "Y", "V", "-"]


def pssm_matrix_from_fasta(input_fasta):
    """
    Computes de matrix of frequencies for the PSSM method from sequence.

    :param input_fasta: inputed fasta file
    :return: returns a PSSM matrix (memory)
    """

    global PATH

    # inputs the fasta file
    motifs = []
    align = AlignIO.read(os.path.join(PATH, input_fasta), "fasta")
    for record in align:
        seq = record.seq
        motifs.append(seq)

    # gets the columns
    columns = []
    for p in range(0, len(motifs[0])):
        column = ""
        for seq in motifs:
            column += seq[p]
        columns.append(column)

    # creates a 2D matrix of amino acids and frequency scores
    # for each amino acid
    matrix_aa = []
    for aa in aa_valid_gap:
        # scores the frequency of that amino acid in that location (position or column)
        matrix_loc = []
        for col in columns:
            # adds a pseudo-count of 0.5 to avoid dividing by zero
            score = (((col.count(aa) * 1.0) + 0.5) / (len(col) + 0.5))
            matrix_loc.append(score)
        matrix_aa.append(matrix_loc)

    return matrix_aa


def pssm_match_score(aa, position, score_matrix):
    """
    Matches a score of an amino acid and its sequence position in a scoring matrix.

    :param aa: amino acid
    :param position: amino acid position
    :param score_matrix: input scoring matrix
    :return: returns a score based on a position indexing
    """

    alphabet = dict()
    alphabet["A"] = 0
    alphabet["R"] = 1
    alphabet["N"] = 2
    alphabet["D"] = 3
    alphabet["C"] = 4
    alphabet["Q"] = 5
    alphabet["E"] = 6
    alphabet["G"] = 7
    alphabet["H"] = 8
    alphabet["I"] = 9
    alphabet["L"] = 10
    alphabet["K"] = 11
    alphabet["M"] = 12
    alphabet["F"] = 13
    alphabet["P"] = 14
    alphabet["S"] = 15
    alphabet["T"] = 16
    alphabet["W"] = 17
    alphabet["Y"] = 18
    alphabet["V"] = 19
    alphabet["-"] = 20
    matched = alphabet[aa]
    return score_matrix[matched][position]


def pssm_scoring(peptide, positives_matrix, negatives_matrix, background_matrix):
    """
    Scores a peptide given matrices of positives, negatives and background.

    :param peptide: input peptide
    :param positives_matrix: frequency matrix of positive peptides
    :param negatives_matrix: frequency matrix of negative peptides
    :param background_matrix: frequency matrix of background peptides
    :return: returns a PSSM score for a peptide
    """

    score = 0.0
    position = -1
    for aa in peptide:
        if aa in aa_valid_gap:
            position += 1
            pos = pssm_match_score(aa, position, positives_matrix)
            neg = pssm_match_score(aa, position, negatives_matrix)
            back = pssm_match_score(aa, position, background_matrix)

            # our definition of PSSM scoring
            score += (pos - neg) * 1.0 / back

    return score / len(peptide)


def pssm_prediction(peptides,
                    positives_pssm="PSSM_POS.fasta",
                    negatives_pssm="PSSM_NEG.fasta",
                    background_pssm="PSSM_BACK.fasta"):
    """
    Makes a final prediction based on PSSM training files.
    This code is used for prediciton of blind datasets, based on the training
    datasets of positives and negatives.

    :param peptides: input peptides
    :param positives_pssm: input positive examples used in training
    :param negatives_pssm: input negative examples used in training
    :param background_pssm: input background examples used in training
    :return: returns PSSM scores for each inputed peptide
    """

    print("Begin PSSM")

    # from methods import load_sqlite, store_sqlite

    pssm_scores = []
    # query the database
    # for peptide in peptides:
    #     try:
    #         score = load_sqlite(peptide, method="PSSM", unique=True)
    #         pssm_scores.append(score)
    #     except:
    #         pass

    if len(peptides) == len(pssm_scores):
        pass
    else:

        positives = pssm_matrix_from_fasta(positives_pssm)
        negatives = pssm_matrix_from_fasta(negatives_pssm)
        background = pssm_matrix_from_fasta(background_pssm)

        pssm_scores = list()
        for peptide in peptides:
            pssm_score = pssm_scoring(peptide, positives, negatives, background)
            pssm_scores.append(pssm_score)

        # save the peptides in db
        # for peptide, score in zip(peptides, pssm_scores):
        #     store_sqlite(peptide, method="PSSM", information=score, save=True)

    print("End PSSM")
    return pssm_scores


def svm_process_header(header):
    """
    "Extract sequence ID and its label from the fasta file.
    Used by PyML.

    :param header:
    :return: returns ID and label
    """

    idd, label_token = header.split()
    return idd.strip(), label_token.split('=')[1]


def svm_prediction(peptides, job_id,
                   input_train="SVM_POS_NEG.fasta"):
    """
    Makes a final prediction based on SVM training files.
    This code is used for prediciton of blind datasets, based on the training
    datasets of positives and negatives.

    :param peptides: input peptides
    :param job_id: random job id assigned prior to start predicting
    :param input_train: input positive and negative examples used in training
    :return: returns SVM scores for each inputed peptide
    """

    print("Begin SVM")

    # from methods import load_sqlite, store_sqlite

    global PATH
    global TMP_PATH

    # suppress SVM output
    devnull = open(os.devnull, 'w')
    sys.stdout, sys.stderr = devnull, devnull

    svm_scores = []
    # query the database
    # for peptide in peptides:
    #     try:
    #         score = load_sqlite(peptide, method="SVM", unique=True)
    #         svm_scores.append(score)
    #     except:
    #         pass

    if len(peptides) == len(svm_scores):
        pass
    else:

        # generate a svm input from the peptides
        rand = job_id
        input_svm = "%s_svm.fasta" % rand
        output_tmp = open(os.path.join(TMP_PATH, input_svm), "w")

        count = 0
        for peptide in peptides:
            count += 1
            output_tmp.write("> %i label=%s\n%s\n" % (count, 1, peptide))
        for peptide in peptides:
            count += 1
            output_tmp.write("> %i label=%s\n%s\n" % (count, -1, peptide))
        output_tmp.close()

        # outputs
        model_svm = "%s_svm_model.txt" % rand

        # train data
        train_data = SequenceData(os.path.join(PATH, input_train), mink=1, maxk=1, maxShift=0,
                                  headerHandler=svm_process_header)
        train_data.attachKernel('cosine')

        cval = 1
        s = SVM(C=cval)
        s.train(train_data)
        s.save(os.path.join(TMP_PATH, model_svm))

        # load trained SVM
        loaded_svm = loadSVM(os.path.join(TMP_PATH, model_svm), train_data)

        # test data
        test_data = SequenceData(os.path.join(TMP_PATH, input_svm), mink=1, maxk=1, maxShift=0,
                                 headerHandler=svm_process_header)
        test_data.attachKernel('cosine')
        results = loaded_svm.test(test_data)

        # print results out
        output_svm = "%s_svm.txt" % rand
        results.toFile(os.path.join(TMP_PATH, output_svm))

        # load results process output (positives + negatives)
        infile = open(os.path.join(TMP_PATH, output_svm), "r")
        inlines = infile.readlines()
        infile.close()
        scores = list()
        for line in inlines:
            line = line.rstrip("\r\n")
            try:
                entry = int(line.split("\t")[0])
                score = float(line.split("\t")[1])
                label = int(line.split("\t")[3])
                if label != "-1":
                    scores.append([entry, score])
            except:
                pass

        # order list
        sorted_scores = sorted(scores, key=lambda scores: scores[0])

        svm_scores = list()
        for score in sorted_scores:
            svm_score = score[1]
            svm_scores.append(svm_score)

        # remove the temporary model files and results
        try:
            os.remove(os.path.join(TMP_PATH, input_svm))
            os.remove(os.path.join(TMP_PATH, model_svm))
            os.remove(os.path.join(TMP_PATH, output_svm))
        except:
            pass

        # save the peptides in db
        # for peptide, score in zip(peptides, svm_scores):
        #     store_sqlite(peptide, method="SVM", information=score, save=True)

    # restore normal output
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__

    print("End SVM")
    return svm_scores


def ann_encoding(aa, method="orthogonal"):
    """
    Encoding for ANN files: it is outputted as a csv file.

    :param aa: amino acid
    :param method: encoding method
    :return: returns an encoding for each amino acid
    """

    aa = aa.upper()
    if method == "orthogonal":
        if aa in aa_valid:
            alphabet = dict()
            alphabet["A"] = "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 "
            alphabet["R"] = "0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 "
            alphabet["N"] = "0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 "
            alphabet["D"] = "0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 "
            alphabet["C"] = "0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 "
            alphabet["Q"] = "0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 "
            alphabet["E"] = "0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 "
            alphabet["G"] = "0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 "
            alphabet["H"] = "0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 "
            alphabet["I"] = "0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 "
            alphabet["L"] = "0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 "
            alphabet["K"] = "0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 "
            alphabet["M"] = "0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 "
            alphabet["F"] = "0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 "
            alphabet["P"] = "0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 "
            alphabet["S"] = "0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 "
            alphabet["T"] = "0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 "
            alphabet["W"] = "0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 "
            alphabet["Y"] = "0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 "
            alphabet["V"] = "0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 "
            matched = alphabet[aa]
        else:
            matched = "0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 "
    else:
        raise ValueError("Please choose one of the available encodings...")
    return matched


def ann_create_csv_from_peptides(peptides, output_file):
    """
    Creates an on the fly csv to load into the /ANN predictor

    :param peptides: list of peptides (formatted)
    :param output_file: output file
    :return: CSV output
    """

    outfile = open(output_file, "w")

    for peptide in peptides:
        encoding = ""
        for aa in peptide:
            encoding += ann_encoding(aa, method="orthogonal")
        outfile.write(encoding + "\n")

    outfile.close()
    return


def ann_prediction(peptides, job_id):
    """
    Makes a final prediction based on ANN training files.
    This code is used for prediciton of blind datasets, based on the training
    datasets of positives and negatives.

    :param peptides: input peptides
    :param job_id: random job id assigned prior to start predicting
    :return: returns ANN scores for each inputed peptide
    """

    print("Begin ANN")

    # from methods import load_sqlite, store_sqlite

    global TMP_PATH

    ann_scores = []
    # query the database
    # for peptide in peptides:
    #     try:
    #         score = load_sqlite(peptide, method="ANN", unique=True)
    #         ann_scores.append(score)
    #     except:
    #         pass

    if len(peptides) == len(ann_scores):
        pass
    else:

        # generate a ann input from the peptides
        rand = job_id
        input_ann = "%s_ann.csv" % rand
        ann_create_csv_from_peptides(peptides, os.path.join(TMP_PATH, input_ann))

        # run "prediciton" for positives and negatives
        output_ann = "%s_ann.txt" % rand
        # [-6:4] => 10 * 20
        len_motif = 200
        len_peptides = len(peptides)
        cmd = str("%s %s %s < %s > %s" % (os.path.join(PATH, "ANN"), len_motif, len_peptides,
                                              os.path.join(TMP_PATH, input_ann),
                                              os.path.join(TMP_PATH, output_ann)))
        os.system(cmd)

        # process output (positives + negatives)
        infile = open(os.path.join(TMP_PATH, output_ann), "r")
        inlines = infile.readlines()
        infile.close()

        ann_scores = list()
        number = len(peptides)
        count = 0
        for line in inlines:
            count += 1
            if count <= number:
                ann_score = line.rstrip("\r\n")
                ann_scores.append(ann_score)

        # remove the temporary model files and results
        try:
            os.remove(os.path.join(TMP_PATH, input_ann))
            os.remove(os.path.join(TMP_PATH, output_ann))
            pass
        except:
            pass

        # save the peptides in db
        # for peptide, score in zip(peptides, ann_scores):
        #     store_sqlite(peptide, method="ANN", information=score, save=True)

    print("End ANN")
    return ann_scores


if __name__ == "__main__":
    pass