#!bin/bash
mount -t securityfs securityfs /sys/kernel/security
/usr/local/bin/gotpm pubkey endorsement
/usr/local/bin/gotpm token --verbose
