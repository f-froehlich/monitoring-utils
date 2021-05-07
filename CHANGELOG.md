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

# 2.1.0
* Checks added:
    * DS18B20

# 2.2.0
* Checks modified:
    * check reboot required now has an option to succeed if reboot is scheduled
* Webserver checks added:
    * check apache proxy requests
* SNMP Checks added:
    * UPS
        * Bad battery packs
        * Battery capacity
        * Battery packs attached
        * Remaining runtime
        * Battery replacement needed
        * Battery status
        * Battery temperature
        * Diagnostic test result
        * Last diagnostic test result time
    * Synology
        * CPU-fan status
        * Disk temperature
        * GPU info
        * Power status
        * RAID status
        * Service running
        * Service used
        * SMART
        * Space IO
        * Storage IO
        * System status
        * Temperature
        * Upgrade
    * Disk load
    * CPU Load
    * Memory Load
        
