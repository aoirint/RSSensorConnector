
## RSSensorConnector

Copy `.env.template` to `.env` and edit environment variables.

If your RSSensorArduino device is not `/dev/ttyACM0`, also edit `devices` section in `docker-compose.yml`.

```sh
sudo docker-compose build
sudo docker-compose up
# sudo docker-compose up -d
```

### Issue?
- Failed to start service when RSSensorArduino device is not connected?
  - Failed to start with `docker-compose up`.
  - (Inspect) When it is auto-started with `docker-compose up -d`?
