EXTRA_TAURUS_PATHS="/usr/lib/python2.7/site-packages/maxwidgets/display /usr/lib/python2.7/site-packages/maxwidgets/extra_guiqwt /usr/lib/python2.7/site-packages/maxwidgets/panel /usr/lib/python2.7/site-packages/maxwidgets/input"

for path in $EXTRA_TAURUS_PATHS; do
    if ! echo $TAURUSQTDESIGNERPATH | grep -q $path; then
        if [ -z ${{TAURUSQTDESIGNERPATH}} ]; then
           TAURUSQTDESIGNERPATH=$path
        else
           TAURUSQTDESIGNERPATH=$TAURUSQTDESIGNERPATH:$path
        fi
    fi
done

export TAURUSQTDESIGNERPATH
