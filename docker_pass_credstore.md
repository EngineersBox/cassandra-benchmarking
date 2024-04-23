# Docker Pass Credential Store

1. `wget https://github.com/docker/docker-credential-helpers/releases/download/v0.8.1/docker-credential-pass-v0.8.1.linux-amd64`
2. `mv docker-credential-pass-v0.8.1.linux-amd64 /usr/local/bin/docker-credential-pass`
3. `chmod +x /usr/local/bin/docker-credential-pass`
4. `sudo apt-get install pass gnupg2`
5. `gpg2 --gen-key` and copy the key ID underneath the pub (`9F53995439D023FD` here in the example:)
```bash
pub   rsa3072 2023-06-13 [SC] [expires: 2025-06-12]
      9F53995439D023FD <-- Copy this bit
uid                      Your Name <Your Email>
sub   rsa3072 2023-06-13 [E] [expires: 2025-06-12]
```
6. `pass init "<Key ID>"`
7. `sed -i '0,/{/s/{/{\n\t"credsStore": "pass",/' ~/.docker/config.json`
8. `pass insert docker-credential-helpers/docker-pass-initialized-check` and set the password to `pass is initialized`
9. `pass show docker-credential-helpers/docker-pass-initialized-check` should show `pass is initialized`
10. `docker login <url> -u <username>` and enter your password
