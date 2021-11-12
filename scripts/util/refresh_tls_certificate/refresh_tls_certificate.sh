#!/bin/bash

# set -x          # Print subcommands to terminal.
set -e          # Fail if any command fails
set -u          # Define variables before usage
set -o pipefail # Make pipes fail


# Options.
letsencrypt_folder="/etc/letsencrypt"
temp_folder="/data"
domain="*.${KHALEESI_DOMAIN}"


echo "Copying letsencrypt configuration..."
cp -a -r "${temp_folder}"/* "${letsencrypt_folder}/"

echo "Requesting certificate for '${domain}'..."
certbot certonly --manual --preferred-challenges=dns --email "${KHALEESI_EMAIL}" --server "https://acme-v02.api.letsencrypt.org/directory" --agree-tos -d "${domain}"

echo "Backing up letsencrypt configuration..."
# shellcheck disable=SC2115
rm -r "${temp_folder}/"*
cp -a -r "${letsencrypt_folder}"/* "${temp_folder}/"
