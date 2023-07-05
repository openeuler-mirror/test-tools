#!/bin/bash

run_remote() {
    cmd_str=$1
    remote_ip=$2
    remote_user=$3

    ssh -n -o "StrictHostKeyChecking=no" "${remote_user}@${remote_ip}" "${cmd_str}"
}

run_remote_return_now() {
    cmd_str=$1
    remote_ip=$2
    remote_user=$3

    ssh -f -n -o "StrictHostKeyChecking=no" "${remote_user}@${remote_ip}" "${cmd_str}"
}

send_remote() {
    src_file=$1
    target_file=$2
    send_ip=$3
    send_user=$4

    scp -r -o "StrictHostKeyChecking=no" "${src_file}" "${send_user}@${send_ip}:${target_file}"
}

delete_remote() {
    delete_file=$1
    remote_ip=$2
    remote_user=$3

    run_remote "rm -rf ${delete_file}" "${remote_ip}" "${remote_user}"
}
