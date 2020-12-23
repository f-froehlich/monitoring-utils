Changelog
=========

# 1.0.0
* Adding some check plugins
    * SSHD security
    * UFW status
    * Existing users
    * Group members
    * Page content
    
# 2.0.0
* Add signals, logging and debugging
* Create status builder with multiline outputs
* Add base plugin
* Add base notification and service notification
* Add web and cli executor
* Add logging to all scripts
* replace exit status with status builder
* Use executors
* Update package structure
* Refactoring checks
* Add Telegram notification

# 2.1.0
* Add some DNS functionality
* Add [Nmap Scan](https://github.com/f-froehlich/nmap-scan) functionality
* Add Nmap script execution functionality
* Checks added:
    * check_ciphers
    * check_open_ports
    * check_dnssec_status
    * check_reboot_required
    * check_spf
