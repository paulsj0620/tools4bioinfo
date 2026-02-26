# tools4bioinfo

# tools4bioinfo
A small collection of lightweight **bioinformatics helper scripts** (mostly Python + shell) for everyday lab tasks such as BED/VCF handling, quick parsers, and simple QC summaries.

> ⚠️ Note: Some scripts in this repo are “quick utilities” and may contain **hard-coded input filenames/paths** (e.g., `example.*.txt`, `chrX_depth.txt`). Treat them as templates and adapt to your environment.

---

## 📦 Contents (Tools)

| Tool | Path | What it does | How to run (example) |
|---|---|---|---|
| **BED modifier** | `bedfile_modifier/bedfile_modifier.py` | Converts/normalizes BED format for downstream usage (see folder README for details). | `python bedfile_modifier.py -i Design.Raw.bed -o Design.Modified.bed` |
| **VCF splitter (by lines)** | `vcf_annotation_splitter/vcf_splitter.py` | Splits a VCF into multiple files by variant-line count, preserving headers. | `python vcf_splitter.py -i input.vcf -c 5000 -o outprefix` |
| **Annotation splitter** | `vcf_annotation_splitter/annotation_splitter.py` | Similar splitter utility; outputs files named with chr/start/end ranges. | `python annotation_splitter.py -i input.vcf -c 5000 -o outprefix` |
| **VCF handler (basic stats)** | `vcffile_handler/vcffile_handler.py` | Provides basic VCF stats (SNP/INDEL count, het/hom, Ts/Tv) via option flag. | `python vcffile_handler.py -i input.vcf -o A` |
| **VCF concordance / genotype check** | `vcffile_handler/vcffile_concordance.py`, `vcffile_handler/vcffile_genotype_check.py` | Helper scripts for VCF comparison / genotype sanity checks (see code). | (edit script / run as needed) |
| **Gender check parser** | `gender_check_parser/gender_check_parser.py` | Converts gender-check results into xls-like output (see code). | (edit script / run as needed) |
| **SGE queue parser** | `sge_queue_parser/sge_queue_parser.py` | Parses Sun Grid Engine queue output for quick summaries. | (edit script / run as needed) |
| **Taxonomy annotation species parser** | `taxnomy_annotation_species_parser/taxnomy_annotation_species_parser.py` | Parses taxonomy annotation and aggregates at species level. | (edit script / run as needed) |
| **Trio analysis filter applier** *(WIP)* | `trio_analysis_filter_applier/trio_analysis_filter_applier.py` | Applies filters to trio SNPEff TSV results (marked as not finished). | `python trio_analysis_filter_applier.py -i input.tsv -o out -t <type> ...` |
| **BAM depth calculator (template)** | `bamfile_depth_calculator/coverage_calculator.sh` | Example bedtools-based depth/coverage calculation template. | `bash coverage_calculator.sh SAMPLE_ID` |
| **Sex chr depth ratio (template)** | `bamfile_depth_calculator/sex_chr_calculator.py` | Computes chrX/chrY depth ratio from precomputed depth tables. | `python sex_chr_calculator.py` |
| **BAM read counter (template)** | `bamfile_read_counter/bamfile_read_counter.py` | Sums `read_count` from a per-target metrics file (example-driven). | `python bamfile_read_counter.py` |

---

## ✅ Requirements

- **Python 3**
- Common UNIX tools (`bash`, `awk`, `sort`) depending on scripts
- For coverage templates: **bedtools** (e.g., `coverageBed`, `groupBy`)

---

## 🚀 Quick Start

Clone and run utilities directly:

```bash
git clone <this-repo-url>
cd tools4bioinfo
python bedfile_modifier/bedfile_modifier.py -i input.bed -o output.bed
```

For scripts that currently use hard-coded filenames, either:
1) Place your input files with the expected names in the same directory, or  
2) Modify the script to accept CLI arguments (recommended).

---

## 🧭 Notes for GitHub Use

- Each tool folder may include its own `README.md` and examples.
- If you want this repo to be more “package-like”, consider:
  - Adding a unified CLI (`tools4bioinfo` entrypoint)
  - Replacing hard-coded filenames with `argparse`
  - Adding `requirements.txt` and minimal tests

---

## 📜 License

Add your preferred license here.

