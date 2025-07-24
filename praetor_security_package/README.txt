# Praetor Security Hardening Package

## How to Use

1. Unzip the package:
   ```
   unzip praetor_security_package.zip
   cd praetor_security_package
   ```

2. Run the main script:
   ```
   sudo bash secure_praetor_machine.sh
   ```

3. During execution:
   - You will set up your encrypted vault (`~/Vault`)
   - You'll be prompted to configure your 2FA with Google Authenticator

4. To start the security monitor:
   ```
   python3 /opt/praetor/hooks/security_monitor.py &
   ```

## Notes
- Logs are sent to the endpoint specified in `/opt/praetor/security_config.json`
- Encrypted vault is mounted at `~/Vault`
