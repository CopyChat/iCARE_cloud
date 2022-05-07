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
. ~/Shell/functions.sh   # ctang's functions

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
local_icare_dir=/gpfs/scratch/le2p/OBS_DATA/icare/ctang/2019/ct
# ======================================


function rename()
# the data downloaded from icare server has a post-fix tag, which 
# is not necessary there, so let remove it:
# this fuction works on the input dir by option "-d"
{
    # get positional argument 1
    dir=$1

    # go to the working position:

    for f in $(ls ${dir})
    do
        echo $f
        echo ${f%Z_*.nc}Z.nc

        mv $dir/$f $dir/${f%_*.nc}.nc
    done
}


function selvar()
# this function selects target variables, since the py code works only on DataArray 
# not on Dataset with multiple variables.
{
    cd $local_icare_dir

    for f in $(ls ${local_icare_dir})
    do
        echo $f

        for var in ct
        do
            echo $var
            cdo selvar,$var $f $var.$f
        done

    done

}

#rename $local_icare_dir

selvar
