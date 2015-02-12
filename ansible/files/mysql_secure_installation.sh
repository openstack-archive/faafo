#!/bin/sh

expect -c "
 
set timeout 3
spawn mysql_secure_installation
 
expect \"Enter current password for root (enter for none):\"
send \"\r\"
 
expect \"root password?\"
send \"y\r\"
 
expect \"New password:\"
send \"secretsecret\r\"
 
expect \"Re-enter new password:\"
send \"secretsecret\r\"
 
expect \"Remove anonymous users?\"
send \"y\r\"
 
expect \"Disallow root login remotely?\"
send \"y\r\"
 
expect \"Remove test database and access to it?\"
send \"y\r\"
 
expect \"Reload privilege tables now?\"
send \"y\r\"
 
expect eof
"

touch /root/mysql_secure_installation.done
