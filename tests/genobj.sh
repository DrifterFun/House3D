
#!bin/sh
for file in /home/fred/zyf/SUNCG_DIR/house/*
do
    if test -d $file
    then
        cd $file
        /home/fred/From_github/SUNCGtoolbox/gaps/bin/x86_64/scn2scn house_change.json house.obj
        echo $file 是文件
    fi
done
