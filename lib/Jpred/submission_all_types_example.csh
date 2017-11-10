#!/bin/csh

perl jpredapi submit mode=single format=raw email=name@domain.com name=TestJob1 silent seq=MQVWPIEGIKKFETLSYLPPLTVEDLLKQIEYLLRSKWVPCLEFSKVGFVYRENHRSPGYYDGRYWTMWKLPMFGCTDATQVLKELEEAKKAYPDAFVRIIGFDNVRQVQLISFIAYKPPGC

perl jpredapi submit mode=single format=raw email=name@domain.com file=single_raw.example name=TestJob2 silent

perl jpredapi submit mode=single format=fasta email=name@domain.com file=single_fasta.example name=TestJob3 silent



perl jpredapi submit mode=msa format=fasta email=name@domain.com file=msa_fasta.example name=TestJob4 silent

perl jpredapi submit mode=msa format=msf email=name@domain.com file=msa_msf.example name=TestJob5 silent

perl jpredapi submit mode=msa format=blc email=name@domain.com file=msa_blc.example name=TestJob6 silent



perl jpredapi submit mode=batch format=fasta email=name@domain.com file=batch_fasta.example name=TestJob7 silent

