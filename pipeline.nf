#!/usr/bin/env nextflow
nextflow.enable.dsl=2

// Define the command-line options to specify the path to VCF files
params.vcf_path = '.test_data/testing_variants_hg38.vcf.gz'
params.hg38 = "/data/project/worthey_lab/datasets_central/human_reference_genome/processed/GRCh38/no_alt_rel20190408/GCA_000001405.15_GRCh38_no_alt_analysis_set.fna"

// Define the Scratch directory
def scratch_dir = System.getenv("USER_SCRATCH") ?: "/tmp"

params.outdir = "${scratch_dir}"

// Define the output directory for intermediate and final results
output_dir = params.outdir

log.info """\
         D I T T O - N F   P I P E L I N E
         ===================================
         hg38             : ${params.hg38}
         into_vcf         : ${params.vcf_path}
         output_dir       : ${output_dir}
         """
         .stripIndent()

// Define the process to normalize a VCF file using bcftools
process normalizeVCF {
  publishDir output_dir, mode:'copy'

  // Define the input channel for the VCF files
  input:
  path into_vcf
  path hg38

  // Define the output channel for the normalized VCF files
  output:
  path "normalized_${into_vcf.baseName}.gz"

  // Modify the path if necessary.
  shell:
  """
  bcftools norm -m-any ${into_vcf} | bcftools norm --threads 2 --check-ref we --fasta-ref ${hg38} -Oz -o "normalized_${into_vcf.baseName}.gz"
  """
}

// Define the process to remove homozygous reference sites using bcftools
process removeHomRefSites {
  publishDir output_dir, mode:'copy'

  // Define the input channel for the normalized VCF file
  input:
  path normalized_vcf

  // Define the output channel for the VCF file with homozygous reference sites removed
  output:
  path "homref_removed_${normalized_vcf.baseName}.gz"

  // Modify the path if necessary.
  script:
  """
  bcftools view --include 'GT[*]="alt"' -Oz -o "homref_removed_${normalized_vcf.baseName}.gz" "${normalized_vcf}"
  """
}

// Define the process to extract the required information from VCF and convert to txt.gz
process extractFromVCF {
  publishDir output_dir, mode:'copy'

  // Define the input channel for the VCF files
  input:
  path homref_vcf

  output:
    path("${homref_vcf.baseName}.txt.gz")

  // Modify the path if necessary.
  shell:
  """
  zcat ${homref_vcf} | grep -v "^#" | cut -d\$'\t' -f1,2,4,5 | grep -v "*" | gzip > ${homref_vcf.baseName}.txt.gz
  """
}

// Define the process to run 'oc' with the specified parameters
process runOC {
  publishDir output_dir, mode:'copy'

  input:
  path var_ch

  output:
    path("${var_ch}.variant.csv")

  shell:
  """
  oc run ${var_ch} -l hg38 -t csv --package mypackage -d ${output_dir}
  cp ${output_dir}/${var_ch}.variant.csv .
  """
}

// Define the process to parse the annotation
process parseAnnotation {
  publishDir output_dir, mode:'copy'

  input:
  path var_ann_ch

  output:
    path("${var_ann_ch.baseName}.csv.gz")

  script:
  """
  python ${baseDir}/src/annotation_parsing/parse.py -i ${var_ann_ch} -e parse -o ${var_ann_ch.baseName}.csv.gz -c ${baseDir}/configs/opencravat_test_config.json
  """
}

// Define the process for prediction
process prediction {
  publishDir output_dir, mode:'copy'

  input:
  path var_parse_ch

  script:
  """
  python ${baseDir}/src/predict/predict.py -i ${var_parse_ch} -o ${output_dir} -c ${baseDir}/configs/col_config.yaml -d ${baseDir}/data/processed/train_data_3_star/
  """
}

// Define the workflow by connecting the processes
// 'into_vcf' will be the channel containing the input VCF files
// Each file in the channel will be processed through the steps defined above.
workflow {
  // Define input channels for the VCF files
  vcfFile = channel.fromPath(params.vcf_path)
  hg38File = channel.fromPath(params.hg38)

  // Process to normalize VCF files
  normalizedVcfFile = normalizeVCF(vcfFile, hg38File)
  // Process to remove homozygous reference sites using the output from normalizeVCF
  // and to extract the required information from VCF and convert to txt.gz
  normalizedVcfFile | flatten | removeHomRefSites | flatten | extractFromVCF
  
  //runOC(extractFromVCF.out)
  //parseAnnotation(runOC.out)
  //prediction(parseAnnotation.out)
}
