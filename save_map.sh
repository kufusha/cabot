#!/bin/bash

function save_map {
    echo "Save the map as $1"
    cd ~/cabot-dev-wip/cabot_sites/cabot_site_kfs/maps
    rosrun map_server map_saver -f $1
}

function copy_map {
    echo "Copy $1.pgm and $1.yaml to cabot_sites2 package"
    cp ~/cabot-dev-wip/cabot_sites/cabot_site_kfs/maps/$1.pgm ~/cabot-dev-wip/cabot_sites2/cabot_site_kfs/maps/$1.pgm
    cp ~/cabot-dev-wip/cabot_sites/cabot_site_kfs/maps/$1.yaml ~/cabot-dev-wip/cabot_sites2/cabot_site_kfs/maps/$1.yaml
}

function replacement_config {
    echo "Replace the map path in config.sh with $1.yaml"
    sed -i "27c map=\$sitedir/maps/$1.yaml" ~/cabot-dev-wip/cabot_sites/cabot_site_kfs/config/config.sh
    sed -i "27c map=\$sitedir/maps/$1.yaml" ~/cabot-dev-wip/cabot_sites2/cabot_site_kfs/config/config.sh
}

map_name=sample_map

while getopts "o:" arg; do
    case $arg in
        o)
            map_name=${OPTARG}
            ;;
    esac
done

save_map ${map_name}
copy_map ${map_name}
replacement_config ${map_name}
