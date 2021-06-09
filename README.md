Create config:
```
user@st2-test:~/FAZAutoST2Pack$ cat /opt/stackstorm/configs/fazautost2pack.yaml
---
  faz_ip: 10.10.10.15
  email_from_address: faz@solidex.by
  email_subject: Notification
  output_format: csv
  password: admin
  server_name: mail
  username: admin
  db_ip: 10.10.10.10
  db_username: user
  db_password: password
  db_connect_str: "()"

user@st2-test:~/FAZAutoST2Pack
```
Register config:
```
sudo st2ctl reload --register-configs
```
Install pack (from local file system):
```
st2 pack install file:///home/user/FAZAutoST2Pack
```

