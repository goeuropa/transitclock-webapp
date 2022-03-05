# Changelog 05-01-2021

1. Added extra information in popup bubbles when clicking icons.
2. Added autorefresh feature which realods entire map object once per 20 seconds.

# Scope of improvements

1. Autorefresh should not reload entire map object but only contents inside map.

# Usage

Edit `transitimeconf.ini` file with appropriate token details and server addresses.
Start the instance using `docker-compose up -d`

If running against kubernetes environment, feed in the container image address to `k8manifests/transitclock.yaml` file and
`kubectl apply -f k8manifests/transitclock.yaml` will start highly available kubernetes deploynment on 30000 port as NodePort service.
