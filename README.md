# DITTO

***!!! For research purposes only !!!***

> **_NOTE:_**  In a past life, DITTO used a different remote Git management provider, [UAB
> Gitlab](https://gitlab.rc.uab.edu/center-for-computational-genomics-and-data-science/sciops/ditto). It was migrated to
> Github in April 2023, and the Gitlab version has been archived.

- [DITTO](#ditto)
    - [Data](#data)
    - [Usage](#usage)
        - [Installation](#installation)
        - [Requirements](#requirements)
        - [Activate conda environment](#activate-conda-environment)
        - [Steps to run DITTO predictions](#steps-to-run-ditto-predictions)
            - [Run VEP annotation](#run-vep-annotation)
            - [Parse VEP annotations](#parse-vep-annotations)
            - [Filter variants for Ditto prediction](#filter-variants-for-ditto-prediction)
            - [DITTO prediction](#ditto-prediction)
            - [Combine with Exomiser scores](#combine-with-exomiser-scores)
        - [Cohort level analysis](#cohort-level-analysis)
    - [Contact information](#contact-information)

**Aim:** We aim to develop a pipeline for accurate and rapid prioritization of variants using patient’s genotype (VCF) and/or phenotype (HPO) information.

## Data

Input for this project is a single sample VCF file. This will be annotated using openCravat and given to Ditto for predictions.

## Usage

### Installation

Installation simply requires fetching the source code. Following are required:

- Git

To fetch source code, change in to directory of your choice and run:

```sh
git clone https://github.com/uab-cgds-worthey/DITTO.git
```

### Requirements

*OS:*

Currently works only in Linux OS. Docker versions may need to be explored later to make it useable in Mac (and
potentially Windows).

*Tools:*

- Anaconda3

### Activate conda environment

Change in to root directory and run the commands below:

```sh
# create conda environment. Needed only the first time.
conda env create --file configs/envs/environment.yaml

# if you need to update existing environment
conda env update --file configs/envs/training.yaml

# activate conda environment
conda activate training
```

### Steps to run DITTO predictions


**Note**: Current version of openCravat that we're using doesn't support "Spanning or overlapping deletions" variants i.e.
variants with `*` in `ALT Allele` column. More on these variants [here](https://gatk.broadinstitute.org/hc/en-us/articles/360035531912-Spanning-or-overlapping-deletions-allele-). These will be ignored when running the pipeline.

#### Run openCravat annotation

Please look at the steps to run openCravat [here](variant_annotation/README.md)


#### Parse openCravat annotations

Please look at the steps to parse openCravat annotations [here](annotation_parsing/README.md)

Example:

`python src/annotation_parsing/parse_annotated_vars.py -i /data/project/worthey_lab/projects/experimental_pipelines/tarun/DITTO/data/external/clinvar_6623.vcf.gz.variant.csv.gz -e parse -o /data/project/worthey_lab/projects/experimental_pipelines/tarun/DITTO/data/interim/clinvar_6623_parsed.csv.gz -c configs/opencravat_train_config.json`


#### Filter variants for Ditto prediction

Filtering step includes imputation and one-hot encoding of columns.

```sh
python src/Ditto/filter.py -i path/to/parsed_vcf_file.tsv -O path/to/output_directory
```

Output from this step includes -

```directory
output_directory/
├── data.csv               <--- used for Ditto predictions
├── Nulls.csv - indicates number of Nulls in each column
├── stats_nssnv.csv - variant stats from the vcf
├── correlation_plot.pdf- Plot to check if any columns are directly correlated (cutoff >0.95)
└── columns.csv - columns before and after filtering step

```

#### Ditto prediction

```sh
python src/Ditto/predict.py  -i path/to/output_directory/data.csv --sample sample_name -o path/to/output_directory/ditto_predictions.csv -o100 .path/to/output_directory/ditto_predictions_100.csv
```

#### Combine with Exomiser scores

If phenotype terms are present for the sample, one could use Exomiser to rank genes and then prioritize Ditto predictions according to the phenotype. Once you have Exomiser scores, please run the following command to combine Exomiser and Ditto scores

```sh
python src/Ditto/combine_scores.py  --raw .path/to/parsed_vcf_file.tsv --sample sample_name --ditto path/to/output_directory/ditto_predictions.csv -ep path/to/exomiser_scores/directory -o .path/to/output_directory/predictions_with_exomiser.csv -o100 path/to/output_directory/predictions_with_exomiser_100.csv
```


### Cohort level analysis

Please refer to [CAGI6-RGP](https://gitlab.rc.uab.edu/center-for-computational-genomics-and-data-science/sciops/mana/mini_projects/rgp_cagi6) project for filtering and annotation of variants as done above for single sample VCF along with calculating Exomiser scores.

For predictions, make necessary directory edits to the snakemake [workflow](workflow/Snakefile) and run the following command.

```sh
sbatch src/predict_variant_score.sh
```

**Note**: The commit used for CAGI6 challenge pipeline is [be97cf5d](https://gitlab.rc.uab.edu/center-for-computational-genomics-and-data-science/sciops/ditto/-/merge_requests/3/diffs?commit_id=be97cf5dbfcb099ac82ef28d5d8b0919f28aed99). It was used along with annotated VCFs  and exomiser scores obtained from [rgp_cagi6 workflow](https://gitlab.rc.uab.edu/center-for-computational-genomics-and-data-science/sciops/mana/mini_projects/rgp_cagi6).


## Contact information

For issues, please send an email with clear description to

Tarun Mamidi    -   tmamidi@uab.edu
