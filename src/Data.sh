#!/bin/bash - 
#======================================================
#
#          FILE: Data.sh
# 
USAGE="./Data.sh"
# 
#   DESCRIPTION: to prepare data for analysis
# 
#       OPTIONS: ---
#  REQUIREMENTS: ---
#          BUGS: --- unknown
#         NOTES: ---
#        AUTHOR: |CHAO.TANG| , |chao.tang.1@gmail.com|
#  ORGANIZATION: 
#       CREATED: 05/02/2022 16:11
#      REVISION: 1.0
#=====================================================
set -o nounset           # Treat unset variables as an error

while getopts ":td:" opt; do
    case $opt in
        t) TEST=1 ;;
        f) dir=$OPTARG;;
        \?) echo $USAGE && exit 1
    esac
done

shift $(($OPTIND - 1))
#----------------------------------------------------
# ======================================
## DEFINITION

# if on my Mac:
local_icare_dir=~/Microsoft_OneDrive/OneDrive/CODE/iCARE_cloud/local_data/icare_dir_ccur

# if on CCuR:
local_icare_dir=/gpfs/scratch/le2p/OBS_DATA/icare/ctang/2021/ct

raw_dir=/gpfs/scratch/le2p/OBS_DATA/icare/raw
ctang_dir=/gpfs/scratch/le2p/OBS_DATA/icare/ctang
# ======================================

function rename()
# the data downloaded from icare server has a post-fix tag, which 
# is not necessary there, so let remove it:
# and sel the var, e.g., ct

{
    year=$1

    echo "year=" $year
    # go to the working position:

    for day_dir in $(ls ${raw_dir}/${year})
    do
        working_dir=${raw_dir}/${year}/${day_dir}
        target_dir=${ctang_dir}/${year}/${day_dir}
        mkdir ${target_dir}
        echo 'working in '  $working_dir

        for f in $(ls ${working_dir})
        do
            input=${working_dir}/$f
            output=${target_dir}/${f%Z_*.nc}Z.nc
            for var in ct
            do
                output=${target_dir}/$var.${f%Z_*.nc}Z.nc
                echo $var, $input, $output >> run.log

                cdo selvar,$var $input $output
            done
        done
    done
}

rename 2021
rename 2019
rename 2018
rename 2022
rename 2017


#function selvar()
## this function selects target variables, since the py code works only on DataArray
## not on Dataset with multiple variables.
#{
#    cd $local_icare_dir
#
#    for f in $(ls ${local_icare_dir})
#    do
#        echo $f
#
#        for var in ct
#        do
#            echo $var
#            cdo selvar,$var $f $var.$f
#        done
#
#    done
#
#}
#
##rename $local_icare_dir
##selvar
