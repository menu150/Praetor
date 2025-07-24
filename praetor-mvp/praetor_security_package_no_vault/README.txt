# Praetor Security Hardening Package (No Vault)

## How to Use

1. Unzip the package:
   ```
   unzip praetor_security_package_no_vault.zip
   cd praetor_security_package
   ```

2. Run the main script:
   ```
   sudo bash secure_praetor_machine.sh
   ```

3. During execution:
   - You'll configure 2FA with Google Authenticator
   - SSH hardening is skipped if `sshd_config` is not found

4. To start the security monitor:
   ```
   python3 /opt/praetor/hooks/security_monitor.py &
   ```

## Notes
- Logs are sent to the endpoint specified in `/opt/praetor/security_config.json`
- Vault encryption has been removed from this version
