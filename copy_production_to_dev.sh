rm latest.dump
heroku pg:backups:capture --app woozup
heroku pg:backups:download --app woozup
pg_restore --verbose --clean --no-acl --no-owner -h localhost -U testdjango -d geoevent latest.dump
