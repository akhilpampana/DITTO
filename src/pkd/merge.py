import pandas as pd
import ray
# Start Ray.
ray.init(ignore_reinit_error=True)
import gc

raw_cols = ['#chr', 'pos(1-based)', 'ref', 'alt', 'aaref', 'aaalt', 'rs_dbSNP', 'hg19_chr', 'hg19_pos(1-based)', 'hg18_chr', 'hg18_pos(1-based)', 'aapos', 'genename', 'Ensembl_geneid', 'Ensembl_transcriptid', 'Ensembl_proteinid', 'Uniprot_acc', 'Uniprot_entry', 'HGVSc_ANNOVAR', 'HGVSp_ANNOVAR', 'HGVSc_snpEff', 'HGVSp_snpEff', 'HGVSc_VEP', 'HGVSp_VEP', 'APPRIS', 'GENCODE_basic', 'TSL', 'VEP_canonical', 'cds_strand', 'refcodon', 'codonpos', 'codon_degeneracy', 'Ancestral_allele', 'AltaiNeandertal', 'Denisova', 'VindijiaNeandertal', 'ChagyrskayaNeandertal', 'SIFT_score', 'SIFT_converted_rankscore', 'SIFT_pred', 'SIFT4G_score', 'SIFT4G_converted_rankscore', 'SIFT4G_pred', 'Polyphen2_HDIV_score', 'Polyphen2_HDIV_rankscore', 'Polyphen2_HDIV_pred', 'Polyphen2_HVAR_score', 'Polyphen2_HVAR_rankscore', 'Polyphen2_HVAR_pred', 'LRT_score', 'LRT_converted_rankscore', 'LRT_pred', 'LRT_Omega', 'MutationTaster_score', 'MutationTaster_converted_rankscore', 'MutationTaster_pred', 'MutationTaster_model', 'MutationTaster_AAE', 'MutationAssessor_score', 'MutationAssessor_rankscore', 'MutationAssessor_pred', 'FATHMM_score', 'FATHMM_converted_rankscore', 'FATHMM_pred', 'PROVEAN_score', 'PROVEAN_converted_rankscore', 'PROVEAN_pred', 'VEST4_score', 'VEST4_rankscore', 'MetaSVM_score', 'MetaSVM_rankscore', 'MetaSVM_pred', 'MetaLR_score', 'MetaLR_rankscore', 'MetaLR_pred', 'Reliability_index', 'MetaRNN_score', 'MetaRNN_rankscore', 'MetaRNN_pred', 'M-CAP_score', 'M-CAP_rankscore', 'M-CAP_pred', 'REVEL_score', 'REVEL_rankscore', 'MutPred_score', 'MutPred_rankscore', 'MutPred_protID', 'MutPred_AAchange', 'MutPred_Top5features', 'MVP_score', 'MVP_rankscore', 'MPC_score', 'MPC_rankscore', 'PrimateAI_score', 'PrimateAI_rankscore', 'PrimateAI_pred', 'DEOGEN2_score', 'DEOGEN2_rankscore', 'DEOGEN2_pred', 'BayesDel_addAF_score', 'BayesDel_addAF_rankscore', 'BayesDel_addAF_pred', 'BayesDel_noAF_score', 'BayesDel_noAF_rankscore', 'BayesDel_noAF_pred', 'ClinPred_score', 'ClinPred_rankscore', 'ClinPred_pred', 'LIST-S2_score', 'LIST-S2_rankscore', 'LIST-S2_pred', 'Aloft_Fraction_transcripts_affected', 'Aloft_prob_Tolerant', 'Aloft_prob_Recessive', 'Aloft_prob_Dominant', 'Aloft_pred', 'Aloft_Confidence', 'CADD_raw', 'CADD_raw_rankscore', 'CADD_phred', 'CADD_raw_hg19', 'CADD_raw_rankscore_hg19', 'CADD_phred_hg19', 'DANN_score', 'DANN_rankscore', 'fathmm-MKL_coding_score', 'fathmm-MKL_coding_rankscore', 'fathmm-MKL_coding_pred', 'fathmm-MKL_coding_group', 'fathmm-XF_coding_score', 'fathmm-XF_coding_rankscore', 'fathmm-XF_coding_pred', 'Eigen-raw_coding', 'Eigen-raw_coding_rankscore', 'Eigen-phred_coding', 'Eigen-PC-raw_coding', 'Eigen-PC-raw_coding_rankscore', 'Eigen-PC-phred_coding', 'GenoCanyon_score', 'GenoCanyon_rankscore', 'integrated_fitCons_score', 'integrated_fitCons_rankscore', 'integrated_confidence_value', 'GM12878_fitCons_score', 'GM12878_fitCons_rankscore', 'GM12878_confidence_value', 'H1-hESC_fitCons_score', 'H1-hESC_fitCons_rankscore', 'H1-hESC_confidence_value', 'HUVEC_fitCons_score', 'HUVEC_fitCons_rankscore', 'HUVEC_confidence_value', 'LINSIGHT', 'LINSIGHT_rankscore', 'GERP++_NR', 'GERP++_RS', 'GERP++_RS_rankscore', 'phyloP100way_vertebrate', 'phyloP100way_vertebrate_rankscore', 'phyloP30way_mammalian', 'phyloP30way_mammalian_rankscore', 'phyloP17way_primate', 'phyloP17way_primate_rankscore', 'phastCons100way_vertebrate', 'phastCons100way_vertebrate_rankscore', 'phastCons30way_mammalian', 'phastCons30way_mammalian_rankscore', 'phastCons17way_primate', 'phastCons17way_primate_rankscore', 'SiPhy_29way_pi', 'SiPhy_29way_logOdds', 'SiPhy_29way_logOdds_rankscore', 'bStatistic', 'bStatistic_converted_rankscore', '1000Gp3_AC', '1000Gp3_AF', '1000Gp3_AFR_AC', '1000Gp3_AFR_AF', '1000Gp3_EUR_AC', '1000Gp3_EUR_AF', '1000Gp3_AMR_AC', '1000Gp3_AMR_AF', '1000Gp3_EAS_AC', '1000Gp3_EAS_AF', '1000Gp3_SAS_AC', '1000Gp3_SAS_AF', 'TWINSUK_AC', 'TWINSUK_AF', 'ALSPAC_AC', 'ALSPAC_AF', 'UK10K_AC', 'UK10K_AF', 'ESP6500_AA_AC', 'ESP6500_AA_AF', 'ESP6500_EA_AC', 'ESP6500_EA_AF', 'ExAC_AC', 'ExAC_AF', 'ExAC_Adj_AC', 'ExAC_Adj_AF', 'ExAC_AFR_AC', 'ExAC_AFR_AF', 'ExAC_AMR_AC', 'ExAC_AMR_AF', 'ExAC_EAS_AC', 'ExAC_EAS_AF', 'ExAC_FIN_AC', 'ExAC_FIN_AF', 'ExAC_NFE_AC', 'ExAC_NFE_AF', 'ExAC_SAS_AC', 'ExAC_SAS_AF', 'ExAC_nonTCGA_AC', 'ExAC_nonTCGA_AF', 'ExAC_nonTCGA_Adj_AC', 'ExAC_nonTCGA_Adj_AF', 'ExAC_nonTCGA_AFR_AC', 'ExAC_nonTCGA_AFR_AF', 'ExAC_nonTCGA_AMR_AC', 'ExAC_nonTCGA_AMR_AF', 'ExAC_nonTCGA_EAS_AC', 'ExAC_nonTCGA_EAS_AF', 'ExAC_nonTCGA_FIN_AC', 'ExAC_nonTCGA_FIN_AF', 'ExAC_nonTCGA_NFE_AC', 'ExAC_nonTCGA_NFE_AF', 'ExAC_nonTCGA_SAS_AC', 'ExAC_nonTCGA_SAS_AF', 'ExAC_nonpsych_AC', 'ExAC_nonpsych_AF', 'ExAC_nonpsych_Adj_AC', 'ExAC_nonpsych_Adj_AF', 'ExAC_nonpsych_AFR_AC', 'ExAC_nonpsych_AFR_AF', 'ExAC_nonpsych_AMR_AC', 'ExAC_nonpsych_AMR_AF', 'ExAC_nonpsych_EAS_AC', 'ExAC_nonpsych_EAS_AF', 'ExAC_nonpsych_FIN_AC', 'ExAC_nonpsych_FIN_AF', 'ExAC_nonpsych_NFE_AC', 'ExAC_nonpsych_NFE_AF', 'ExAC_nonpsych_SAS_AC', 'ExAC_nonpsych_SAS_AF', 'gnomAD_exomes_flag', 'gnomAD_exomes_AC', 'gnomAD_exomes_AN', 'gnomAD_exomes_AF', 'gnomAD_exomes_nhomalt', 'gnomAD_exomes_AFR_AC', 'gnomAD_exomes_AFR_AN', 'gnomAD_exomes_AFR_AF', 'gnomAD_exomes_AFR_nhomalt', 'gnomAD_exomes_AMR_AC', 'gnomAD_exomes_AMR_AN', 'gnomAD_exomes_AMR_AF', 'gnomAD_exomes_AMR_nhomalt', 'gnomAD_exomes_ASJ_AC', 'gnomAD_exomes_ASJ_AN', 'gnomAD_exomes_ASJ_AF', 'gnomAD_exomes_ASJ_nhomalt', 'gnomAD_exomes_EAS_AC', 'gnomAD_exomes_EAS_AN', 'gnomAD_exomes_EAS_AF', 'gnomAD_exomes_EAS_nhomalt', 'gnomAD_exomes_FIN_AC', 'gnomAD_exomes_FIN_AN', 'gnomAD_exomes_FIN_AF', 'gnomAD_exomes_FIN_nhomalt', 'gnomAD_exomes_NFE_AC', 'gnomAD_exomes_NFE_AN', 'gnomAD_exomes_NFE_AF', 'gnomAD_exomes_NFE_nhomalt', 'gnomAD_exomes_SAS_AC', 'gnomAD_exomes_SAS_AN', 'gnomAD_exomes_SAS_AF', 'gnomAD_exomes_SAS_nhomalt', 'gnomAD_exomes_POPMAX_AC', 'gnomAD_exomes_POPMAX_AN', 'gnomAD_exomes_POPMAX_AF', 'gnomAD_exomes_POPMAX_nhomalt', 'gnomAD_exomes_controls_AC', 'gnomAD_exomes_controls_AN', 'gnomAD_exomes_controls_AF', 'gnomAD_exomes_controls_nhomalt', 'gnomAD_exomes_non_neuro_AC', 'gnomAD_exomes_non_neuro_AN', 'gnomAD_exomes_non_neuro_AF', 'gnomAD_exomes_non_neuro_nhomalt', 'gnomAD_exomes_non_cancer_AC', 'gnomAD_exomes_non_cancer_AN', 'gnomAD_exomes_non_cancer_AF', 'gnomAD_exomes_non_cancer_nhomalt', 'gnomAD_exomes_non_topmed_AC', 'gnomAD_exomes_non_topmed_AN', 'gnomAD_exomes_non_topmed_AF', 'gnomAD_exomes_non_topmed_nhomalt', 'gnomAD_exomes_controls_AFR_AC', 'gnomAD_exomes_controls_AFR_AN', 'gnomAD_exomes_controls_AFR_AF', 'gnomAD_exomes_controls_AFR_nhomalt', 'gnomAD_exomes_controls_AMR_AC', 'gnomAD_exomes_controls_AMR_AN', 'gnomAD_exomes_controls_AMR_AF', 'gnomAD_exomes_controls_AMR_nhomalt', 'gnomAD_exomes_controls_ASJ_AC', 'gnomAD_exomes_controls_ASJ_AN', 'gnomAD_exomes_controls_ASJ_AF', 'gnomAD_exomes_controls_ASJ_nhomalt', 'gnomAD_exomes_controls_EAS_AC', 'gnomAD_exomes_controls_EAS_AN', 'gnomAD_exomes_controls_EAS_AF', 'gnomAD_exomes_controls_EAS_nhomalt', 'gnomAD_exomes_controls_FIN_AC', 'gnomAD_exomes_controls_FIN_AN', 'gnomAD_exomes_controls_FIN_AF', 'gnomAD_exomes_controls_FIN_nhomalt', 'gnomAD_exomes_controls_NFE_AC', 'gnomAD_exomes_controls_NFE_AN', 'gnomAD_exomes_controls_NFE_AF', 'gnomAD_exomes_controls_NFE_nhomalt', 'gnomAD_exomes_controls_SAS_AC', 'gnomAD_exomes_controls_SAS_AN', 'gnomAD_exomes_controls_SAS_AF', 'gnomAD_exomes_controls_SAS_nhomalt', 'gnomAD_exomes_controls_POPMAX_AC', 'gnomAD_exomes_controls_POPMAX_AN', 'gnomAD_exomes_controls_POPMAX_AF', 'gnomAD_exomes_controls_POPMAX_nhomalt', 'gnomAD_exomes_non_neuro_AFR_AC', 'gnomAD_exomes_non_neuro_AFR_AN', 'gnomAD_exomes_non_neuro_AFR_AF', 'gnomAD_exomes_non_neuro_AFR_nhomalt', 'gnomAD_exomes_non_neuro_AMR_AC', 'gnomAD_exomes_non_neuro_AMR_AN', 'gnomAD_exomes_non_neuro_AMR_AF', 'gnomAD_exomes_non_neuro_AMR_nhomalt', 'gnomAD_exomes_non_neuro_ASJ_AC', 'gnomAD_exomes_non_neuro_ASJ_AN', 'gnomAD_exomes_non_neuro_ASJ_AF', 'gnomAD_exomes_non_neuro_ASJ_nhomalt', 'gnomAD_exomes_non_neuro_EAS_AC', 'gnomAD_exomes_non_neuro_EAS_AN', 'gnomAD_exomes_non_neuro_EAS_AF', 'gnomAD_exomes_non_neuro_EAS_nhomalt', 'gnomAD_exomes_non_neuro_FIN_AC', 'gnomAD_exomes_non_neuro_FIN_AN', 'gnomAD_exomes_non_neuro_FIN_AF', 'gnomAD_exomes_non_neuro_FIN_nhomalt', 'gnomAD_exomes_non_neuro_NFE_AC', 'gnomAD_exomes_non_neuro_NFE_AN', 'gnomAD_exomes_non_neuro_NFE_AF', 'gnomAD_exomes_non_neuro_NFE_nhomalt', 'gnomAD_exomes_non_neuro_SAS_AC', 'gnomAD_exomes_non_neuro_SAS_AN', 'gnomAD_exomes_non_neuro_SAS_AF', 'gnomAD_exomes_non_neuro_SAS_nhomalt', 'gnomAD_exomes_non_neuro_POPMAX_AC', 'gnomAD_exomes_non_neuro_POPMAX_AN', 'gnomAD_exomes_non_neuro_POPMAX_AF', 'gnomAD_exomes_non_neuro_POPMAX_nhomalt', 'gnomAD_exomes_non_cancer_AFR_AC', 'gnomAD_exomes_non_cancer_AFR_AN', 'gnomAD_exomes_non_cancer_AFR_AF', 'gnomAD_exomes_non_cancer_AFR_nhomalt', 'gnomAD_exomes_non_cancer_AMR_AC', 'gnomAD_exomes_non_cancer_AMR_AN', 'gnomAD_exomes_non_cancer_AMR_AF', 'gnomAD_exomes_non_cancer_AMR_nhomalt', 'gnomAD_exomes_non_cancer_ASJ_AC', 'gnomAD_exomes_non_cancer_ASJ_AN', 'gnomAD_exomes_non_cancer_ASJ_AF', 'gnomAD_exomes_non_cancer_ASJ_nhomalt', 'gnomAD_exomes_non_cancer_EAS_AC', 'gnomAD_exomes_non_cancer_EAS_AN', 'gnomAD_exomes_non_cancer_EAS_AF', 'gnomAD_exomes_non_cancer_EAS_nhomalt', 'gnomAD_exomes_non_cancer_FIN_AC', 'gnomAD_exomes_non_cancer_FIN_AN', 'gnomAD_exomes_non_cancer_FIN_AF', 'gnomAD_exomes_non_cancer_FIN_nhomalt', 'gnomAD_exomes_non_cancer_NFE_AC', 'gnomAD_exomes_non_cancer_NFE_AN', 'gnomAD_exomes_non_cancer_NFE_AF', 'gnomAD_exomes_non_cancer_NFE_nhomalt', 'gnomAD_exomes_non_cancer_SAS_AC', 'gnomAD_exomes_non_cancer_SAS_AN', 'gnomAD_exomes_non_cancer_SAS_AF', 'gnomAD_exomes_non_cancer_SAS_nhomalt', 'gnomAD_exomes_non_cancer_POPMAX_AC', 'gnomAD_exomes_non_cancer_POPMAX_AN', 'gnomAD_exomes_non_cancer_POPMAX_AF', 'gnomAD_exomes_non_cancer_POPMAX_nhomalt', 'gnomAD_exomes_non_topmed_AFR_AC', 'gnomAD_exomes_non_topmed_AFR_AN', 'gnomAD_exomes_non_topmed_AFR_AF', 'gnomAD_exomes_non_topmed_AFR_nhomalt', 'gnomAD_exomes_non_topmed_AMR_AC', 'gnomAD_exomes_non_topmed_AMR_AN', 'gnomAD_exomes_non_topmed_AMR_AF', 'gnomAD_exomes_non_topmed_AMR_nhomalt', 'gnomAD_exomes_non_topmed_ASJ_AC', 'gnomAD_exomes_non_topmed_ASJ_AN', 'gnomAD_exomes_non_topmed_ASJ_AF', 'gnomAD_exomes_non_topmed_ASJ_nhomalt', 'gnomAD_exomes_non_topmed_EAS_AC', 'gnomAD_exomes_non_topmed_EAS_AN', 'gnomAD_exomes_non_topmed_EAS_AF', 'gnomAD_exomes_non_topmed_EAS_nhomalt', 'gnomAD_exomes_non_topmed_FIN_AC', 'gnomAD_exomes_non_topmed_FIN_AN', 'gnomAD_exomes_non_topmed_FIN_AF', 'gnomAD_exomes_non_topmed_FIN_nhomalt', 'gnomAD_exomes_non_topmed_NFE_AC', 'gnomAD_exomes_non_topmed_NFE_AN', 'gnomAD_exomes_non_topmed_NFE_AF', 'gnomAD_exomes_non_topmed_NFE_nhomalt', 'gnomAD_exomes_non_topmed_SAS_AC', 'gnomAD_exomes_non_topmed_SAS_AN', 'gnomAD_exomes_non_topmed_SAS_AF', 'gnomAD_exomes_non_topmed_SAS_nhomalt', 'gnomAD_exomes_non_topmed_POPMAX_AC', 'gnomAD_exomes_non_topmed_POPMAX_AN', 'gnomAD_exomes_non_topmed_POPMAX_AF', 'gnomAD_exomes_non_topmed_POPMAX_nhomalt', 'gnomAD_genomes_flag', 'gnomAD_genomes_AC', 'gnomAD_genomes_AN', 'gnomAD_genomes_AF', 'gnomAD_genomes_nhomalt', 'gnomAD_genomes_POPMAX_AC', 'gnomAD_genomes_POPMAX_AN', 'gnomAD_genomes_POPMAX_AF', 'gnomAD_genomes_POPMAX_nhomalt', 'gnomAD_genomes_AFR_AC', 'gnomAD_genomes_AFR_AN', 'gnomAD_genomes_AFR_AF', 'gnomAD_genomes_AFR_nhomalt', 'gnomAD_genomes_AMI_AC', 'gnomAD_genomes_AMI_AN', 'gnomAD_genomes_AMI_AF', 'gnomAD_genomes_AMI_nhomalt', 'gnomAD_genomes_AMR_AC', 'gnomAD_genomes_AMR_AN', 'gnomAD_genomes_AMR_AF', 'gnomAD_genomes_AMR_nhomalt', 'gnomAD_genomes_ASJ_AC', 'gnomAD_genomes_ASJ_AN', 'gnomAD_genomes_ASJ_AF', 'gnomAD_genomes_ASJ_nhomalt', 'gnomAD_genomes_EAS_AC', 'gnomAD_genomes_EAS_AN', 'gnomAD_genomes_EAS_AF', 'gnomAD_genomes_EAS_nhomalt', 'gnomAD_genomes_FIN_AC', 'gnomAD_genomes_FIN_AN', 'gnomAD_genomes_FIN_AF', 'gnomAD_genomes_FIN_nhomalt', 'gnomAD_genomes_MID_AC', 'gnomAD_genomes_MID_AN', 'gnomAD_genomes_MID_AF', 'gnomAD_genomes_MID_nhomalt', 'gnomAD_genomes_NFE_AC', 'gnomAD_genomes_NFE_AN', 'gnomAD_genomes_NFE_AF', 'gnomAD_genomes_NFE_nhomalt', 'gnomAD_genomes_SAS_AC', 'gnomAD_genomes_SAS_AN', 'gnomAD_genomes_SAS_AF', 'gnomAD_genomes_SAS_nhomalt', 'gnomAD_genomes_controls_and_biobanks_AC', 'gnomAD_genomes_controls_and_biobanks_AN', 'gnomAD_genomes_controls_and_biobanks_AF', 'gnomAD_genomes_controls_and_biobanks_nhomalt', 'gnomAD_genomes_non_neuro_AC', 'gnomAD_genomes_non_neuro_AN', 'gnomAD_genomes_non_neuro_AF', 'gnomAD_genomes_non_neuro_nhomalt', 'gnomAD_genomes_non_cancer_AC', 'gnomAD_genomes_non_cancer_AN', 'gnomAD_genomes_non_cancer_AF', 'gnomAD_genomes_non_cancer_nhomalt', 'gnomAD_genomes_non_topmed_AC', 'gnomAD_genomes_non_topmed_AN', 'gnomAD_genomes_non_topmed_AF', 'gnomAD_genomes_non_topmed_nhomalt', 'gnomAD_genomes_controls_and_biobanks_AFR_AC', 'gnomAD_genomes_controls_and_biobanks_AFR_AN', 'gnomAD_genomes_controls_and_biobanks_AFR_AF', 'gnomAD_genomes_controls_and_biobanks_AFR_nhomalt', 'gnomAD_genomes_controls_and_biobanks_AMI_AC', 'gnomAD_genomes_controls_and_biobanks_AMI_AN', 'gnomAD_genomes_controls_and_biobanks_AMI_AF', 'gnomAD_genomes_controls_and_biobanks_AMI_nhomalt', 'gnomAD_genomes_controls_and_biobanks_AMR_AC', 'gnomAD_genomes_controls_and_biobanks_AMR_AN', 'gnomAD_genomes_controls_and_biobanks_AMR_AF', 'gnomAD_genomes_controls_and_biobanks_AMR_nhomalt', 'gnomAD_genomes_controls_and_biobanks_ASJ_AC', 'gnomAD_genomes_controls_and_biobanks_ASJ_AN', 'gnomAD_genomes_controls_and_biobanks_ASJ_AF', 'gnomAD_genomes_controls_and_biobanks_ASJ_nhomalt', 'gnomAD_genomes_controls_and_biobanks_EAS_AC', 'gnomAD_genomes_controls_and_biobanks_EAS_AN', 'gnomAD_genomes_controls_and_biobanks_EAS_AF', 'gnomAD_genomes_controls_and_biobanks_EAS_nhomalt', 'gnomAD_genomes_controls_and_biobanks_FIN_AC', 'gnomAD_genomes_controls_and_biobanks_FIN_AN', 'gnomAD_genomes_controls_and_biobanks_FIN_AF', 'gnomAD_genomes_controls_and_biobanks_FIN_nhomalt', 'gnomAD_genomes_controls_and_biobanks_MID_AC', 'gnomAD_genomes_controls_and_biobanks_MID_AN', 'gnomAD_genomes_controls_and_biobanks_MID_AF', 'gnomAD_genomes_controls_and_biobanks_MID_nhomalt', 'gnomAD_genomes_controls_and_biobanks_NFE_AC', 'gnomAD_genomes_controls_and_biobanks_NFE_AN', 'gnomAD_genomes_controls_and_biobanks_NFE_AF', 'gnomAD_genomes_controls_and_biobanks_NFE_nhomalt', 'gnomAD_genomes_controls_and_biobanks_SAS_AC', 'gnomAD_genomes_controls_and_biobanks_SAS_AN', 'gnomAD_genomes_controls_and_biobanks_SAS_AF', 'gnomAD_genomes_controls_and_biobanks_SAS_nhomalt', 'gnomAD_genomes_non_neuro_AFR_AC', 'gnomAD_genomes_non_neuro_AFR_AN', 'gnomAD_genomes_non_neuro_AFR_AF', 'gnomAD_genomes_non_neuro_AFR_nhomalt', 'gnomAD_genomes_non_neuro_AMI_AC', 'gnomAD_genomes_non_neuro_AMI_AN', 'gnomAD_genomes_non_neuro_AMI_AF', 'gnomAD_genomes_non_neuro_AMI_nhomalt', 'gnomAD_genomes_non_neuro_AMR_AC', 'gnomAD_genomes_non_neuro_AMR_AN', 'gnomAD_genomes_non_neuro_AMR_AF', 'gnomAD_genomes_non_neuro_AMR_nhomalt', 'gnomAD_genomes_non_neuro_ASJ_AC', 'gnomAD_genomes_non_neuro_ASJ_AN', 'gnomAD_genomes_non_neuro_ASJ_AF', 'gnomAD_genomes_non_neuro_ASJ_nhomalt', 'gnomAD_genomes_non_neuro_EAS_AC', 'gnomAD_genomes_non_neuro_EAS_AN', 'gnomAD_genomes_non_neuro_EAS_AF', 'gnomAD_genomes_non_neuro_EAS_nhomalt', 'gnomAD_genomes_non_neuro_FIN_AC', 'gnomAD_genomes_non_neuro_FIN_AN', 'gnomAD_genomes_non_neuro_FIN_AF', 'gnomAD_genomes_non_neuro_FIN_nhomalt', 'gnomAD_genomes_non_neuro_MID_AC', 'gnomAD_genomes_non_neuro_MID_AN', 'gnomAD_genomes_non_neuro_MID_AF', 'gnomAD_genomes_non_neuro_MID_nhomalt', 'gnomAD_genomes_non_neuro_NFE_AC', 'gnomAD_genomes_non_neuro_NFE_AN', 'gnomAD_genomes_non_neuro_NFE_AF', 'gnomAD_genomes_non_neuro_NFE_nhomalt', 'gnomAD_genomes_non_neuro_SAS_AC', 'gnomAD_genomes_non_neuro_SAS_AN', 'gnomAD_genomes_non_neuro_SAS_AF', 'gnomAD_genomes_non_neuro_SAS_nhomalt', 'gnomAD_genomes_non_cancer_AFR_AC', 'gnomAD_genomes_non_cancer_AFR_AN', 'gnomAD_genomes_non_cancer_AFR_AF', 'gnomAD_genomes_non_cancer_AFR_nhomalt', 'gnomAD_genomes_non_cancer_AMI_AC', 'gnomAD_genomes_non_cancer_AMI_AN', 'gnomAD_genomes_non_cancer_AMI_AF', 'gnomAD_genomes_non_cancer_AMI_nhomalt', 'gnomAD_genomes_non_cancer_AMR_AC', 'gnomAD_genomes_non_cancer_AMR_AN', 'gnomAD_genomes_non_cancer_AMR_AF', 'gnomAD_genomes_non_cancer_AMR_nhomalt', 'gnomAD_genomes_non_cancer_ASJ_AC', 'gnomAD_genomes_non_cancer_ASJ_AN', 'gnomAD_genomes_non_cancer_ASJ_AF', 'gnomAD_genomes_non_cancer_ASJ_nhomalt', 'gnomAD_genomes_non_cancer_EAS_AC', 'gnomAD_genomes_non_cancer_EAS_AN', 'gnomAD_genomes_non_cancer_EAS_AF', 'gnomAD_genomes_non_cancer_EAS_nhomalt', 'gnomAD_genomes_non_cancer_FIN_AC', 'gnomAD_genomes_non_cancer_FIN_AN', 'gnomAD_genomes_non_cancer_FIN_AF', 'gnomAD_genomes_non_cancer_FIN_nhomalt', 'gnomAD_genomes_non_cancer_MID_AC', 'gnomAD_genomes_non_cancer_MID_AN', 'gnomAD_genomes_non_cancer_MID_AF', 'gnomAD_genomes_non_cancer_MID_nhomalt', 'gnomAD_genomes_non_cancer_NFE_AC', 'gnomAD_genomes_non_cancer_NFE_AN', 'gnomAD_genomes_non_cancer_NFE_AF', 'gnomAD_genomes_non_cancer_NFE_nhomalt', 'gnomAD_genomes_non_cancer_SAS_AC', 'gnomAD_genomes_non_cancer_SAS_AN', 'gnomAD_genomes_non_cancer_SAS_AF', 'gnomAD_genomes_non_cancer_SAS_nhomalt', 'gnomAD_genomes_non_topmed_AFR_AC', 'gnomAD_genomes_non_topmed_AFR_AN', 'gnomAD_genomes_non_topmed_AFR_AF', 'gnomAD_genomes_non_topmed_AFR_nhomalt', 'gnomAD_genomes_non_topmed_AMI_AC', 'gnomAD_genomes_non_topmed_AMI_AN', 'gnomAD_genomes_non_topmed_AMI_AF', 'gnomAD_genomes_non_topmed_AMI_nhomalt', 'gnomAD_genomes_non_topmed_AMR_AC', 'gnomAD_genomes_non_topmed_AMR_AN', 'gnomAD_genomes_non_topmed_AMR_AF', 'gnomAD_genomes_non_topmed_AMR_nhomalt', 'gnomAD_genomes_non_topmed_ASJ_AC', 'gnomAD_genomes_non_topmed_ASJ_AN', 'gnomAD_genomes_non_topmed_ASJ_AF', 'gnomAD_genomes_non_topmed_ASJ_nhomalt', 'gnomAD_genomes_non_topmed_EAS_AC', 'gnomAD_genomes_non_topmed_EAS_AN', 'gnomAD_genomes_non_topmed_EAS_AF', 'gnomAD_genomes_non_topmed_EAS_nhomalt', 'gnomAD_genomes_non_topmed_FIN_AC', 'gnomAD_genomes_non_topmed_FIN_AN', 'gnomAD_genomes_non_topmed_FIN_AF', 'gnomAD_genomes_non_topmed_FIN_nhomalt', 'gnomAD_genomes_non_topmed_MID_AC', 'gnomAD_genomes_non_topmed_MID_AN', 'gnomAD_genomes_non_topmed_MID_AF', 'gnomAD_genomes_non_topmed_MID_nhomalt', 'gnomAD_genomes_non_topmed_NFE_AC', 'gnomAD_genomes_non_topmed_NFE_AN', 'gnomAD_genomes_non_topmed_NFE_AF', 'gnomAD_genomes_non_topmed_NFE_nhomalt', 'gnomAD_genomes_non_topmed_SAS_AC', 'gnomAD_genomes_non_topmed_SAS_AN', 'gnomAD_genomes_non_topmed_SAS_AF', 'gnomAD_genomes_non_topmed_SAS_nhomalt', 'clinvar_id', 'clinvar_clnsig', 'clinvar_trait', 'clinvar_review', 'clinvar_hgvs', 'clinvar_var_source', 'clinvar_MedGen_id', 'clinvar_OMIM_id', 'clinvar_Orphanet_id', 'Interpro_domain', 'GTEx_V8_gene', 'GTEx_V8_tissue', 'Geuvadis_eQTL_target_gene']

@ray.remote  # (num_cpus=9)
def gene_integration(gene,raw_cols):
    ditto = pd.read_csv(f'/data/project/worthey_lab/projects/experimental_pipelines/tarun/ditto/data/processed/Ditto/{gene}/dbnsfp_{gene}_ditto_predictions.csv.gz')
    #ditto['#chr'] = ditto['#chr'].astype('int64')
    ditto['pos(1-based)'] = ditto['pos(1-based)'].astype('int64')
    dbnsfp = pd.read_csv(f'/data/project/worthey_lab/projects/experimental_pipelines/tarun/ditto/data/processed/Ditto/{gene}/dbNSFP_{gene}_variants.tsv.gz', header=None, sep='\t', names=raw_cols)
    #dbnsfp['#chr'] = dbnsfp['#chr'].astype('int64')
    dbnsfp['pos(1-based)'] = dbnsfp['pos(1-based)'].astype('int64')
    dbnsfp = dbnsfp[['#chr','pos(1-based)','ref','alt', 'aapos', 'aaref', 'aaalt',"CADD_phred",
                "gnomAD_genomes_AF","HGVSc_VEP","HGVSp_VEP","Ensembl_transcriptid"]]
    ditto = ditto.merge(dbnsfp, on=['#chr','pos(1-based)','ref','alt','Ensembl_transcriptid'], how='left')

    ditto = ditto[['#chr', 'pos(1-based)', 'ref', 'alt', 'cds_strand', 'genename',
           'Ensembl_geneid', 'Ensembl_transcriptid', 'Ensembl_proteinid', 'Uniprot_acc',
           'clinvar_clnsig', 'clinvar_review', 'Interpro_domain',
           'Ditto_Deleterious', 'aapos',
           'aaref', 'aaalt', 'CADD_phred', 'gnomAD_genomes_AF', 'HGVSc_VEP',
           'HGVSp_VEP']]

    ditto.to_csv(f'/data/project/worthey_lab/projects/experimental_pipelines/tarun/ditto/data/processed/Ditto/{gene}/{gene}_Integrated.csv.gz', index=False)
    ditto.to_csv(f'/data/project/worthey_lab/projects/experimental_pipelines/tarun/ditto/data/processed/ciliopathy_genes/{gene}_Integrated.csv', index=False)

if __name__ == "__main__":

    gene_list = ["AHI1","DCTN1","LRPPRC","PCNT","STOM","ATXN10","CEP97","DCTN2","MKS1","PDE6D","TBC1D4","B9D1","CFAP52","EIF5B","PIBF1","TCTN1","B9D2","COX6C","IFT88","MYL6","TMEM216","BCAR1","INPP5E","MYL6B","TMEM67","CALM1","INVS","PTPN11","TTC21B","CC2D2A","IQCB1","NME7","RAC1","TTC26","CCDC65","IQGAP1","NPHP1","RIBC1","UNC119B","CCP110","IQGAP2","NPHP3","RPGR","CEP164","IQGAP3","NPHP4","RPGRIP1","WDR35","CEP290","KIAA0753","RPGRIP1L","ZMYND12","CEP89","KIF3A","OFD1","SDCCAG8"]
    remote_ml = [
        gene_integration.remote(gene,raw_cols)

        for gene in gene_list
    ]
    ray.get(remote_ml)
    gc.collect()
