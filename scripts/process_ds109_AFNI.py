# Analysis of ds001 with AFNI

import os

from lib.afni_processing import copy_raw, create_afni_onset_files
from lib.afni_processing import run_subject_level_analyses
from lib.afni_processing import run_group_level_analysis
from lib.afni_processing import run_permutation_test
from lib.afni_processing import mean_mni_images
from lib.afni_processing import run_SSWarper

raw_dir = '/home/maullz/NIDM-Ex/BIDS_Data/DATA/BIDS/ds000109_R2.0.1'

# Set default orientation to origin (instead of standardised space) for
# ambiguous NIfTi (required for ds001)
os.environ["AFNI_NIFTI_VIEW"] = "orig"
results_dir = \
    '/home/maullz/NIDM-Ex/BIDS_Data/RESULTS/SOFTWARE_COMPARISON/ds109'

afni_dir = os.path.join(results_dir, 'AFNI')

if not os.path.isdir(afni_dir):
    os.mkdir(afni_dir)

preproc_dir = os.path.join(afni_dir, 'PREPROCESSING')
level1_dir = os.path.join(afni_dir, 'LEVEL1')
level2_dir = os.path.join(afni_dir, 'LEVEL2')
perm_dir = os.path.join(level2_dir, 'permutation_test')
mni_dir = os.path.join(afni_dir, 'mean_mni_images')

# Set default orientation to origin (instead of standardised space) for
# ambiguous NIfTi (required for ds001)
os.environ["AFNI_NIFTI_VIEW"] = "orig"

# Specify the number of functional volumes ignored in the study
TR = 2
num_ignored_volumes = 0

# Specify the TR that will be removed from onesets, equal to num_ignored_volumes*TR
removed_TR_time = num_ignored_volumes*TR 

# Specify the subjects of interest from the raw data
subject_ids = [1, 2, 3, 8, 9, 10, 11, 14, 15, 17, 18, 21, 22, 26, 27, 28, 30, 31, 32, 43, 48]
subject_ids = ['{num:02d}'.format(num=x) for x in subject_ids]

cwd = os.path.dirname(os.path.realpath(__file__))

# Copy raw anatomical and functional data to the preprocessing directory and
# run BET on the anatomical images
copy_raw(raw_dir, preproc_dir, subject_ids)

# Directory to store the onset files
onset_dir = os.path.join(afni_dir, 'ONSETS')

# Define conditions and parametric modulations (if any)
# FORMAT
#   {VariableLabel,{TrialType,Durations}}
#   {{VariableLabel,VariableModLabel},{TrialType,Duration,Amplitude}}
conditions = (
    ('false_belief_story', ('false belief story', 'duration')),
    ('false_belief_question', ('false belief question', 'duration')),
    ('false_photo_story', ('false photo story', 'duration')),
    ('false_photo_question', ('false photo question', 'duration')))

# Create onset files based on BIDS tsv files
cond_files = create_afni_onset_files(raw_dir, onset_dir, conditions, removed_TR_time, subject_ids)

SSWarper_template = os.path.join(cwd, 'lib', 'template_AFNI_SSWarper')
sub_level_template = os.path.join(cwd, 'lib', 'template_ds109_AFNI_level1')
grp_level_template = os.path.join(cwd, 'lib', 'template_ds109_AFNI_level2')
perm_template = os.path.join(cwd, 'lib', 'template_ds109_AFNI_perm_test')

# Run SSWarper AFNI command on each subject to strip skull and warp to MNI template
run_SSWarper(preproc_dir, SSWarper_template)

# Run a GLM combining all the fMRI runs of each subject
run_subject_level_analyses(preproc_dir, onset_dir, level1_dir, sub_level_template)

# Run the group-level GLM
run_group_level_analysis(level1_dir, level2_dir, grp_level_template)

# Run a permutation test
run_permutation_test(level1_dir, perm_dir, perm_template)

# Create mean and standard deviations maps of the mean func and anat images in MNI space
mean_mni_images(preproc_dir, level1_dir, mni_dir)
