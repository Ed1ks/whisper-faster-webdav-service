#!/bin/bash
if [ "${UID}" = "0" ]; then
  groupadd -f -g "${PGID}" nonroot
  useradd -u "${PUID}" -g "${PGID}" nonroot
  chown -R "${PUID}":"${PGID}" /audiotagger
  exec su "nonroot" "$0" -- "$@"  # user changin
fi

whoami

# --this part will be executed by user nonroot--

exec "$@"