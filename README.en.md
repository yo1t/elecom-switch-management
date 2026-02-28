# ELECOM EHB-SQ2A08 Switch Management Scripts

[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue?logo=github)](https://github.com/yo1t/elecom-switch-management)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://github.com/yo1t/elecom-switch-management/blob/main/LICENSE)
[![Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)

> **Repository**: [https://github.com/yo1t/elecom-switch-management](https://github.com/yo1t/elecom-switch-management)

Python scripts for managing ELECOM EHB-SQ2A08 switching hub. Retrieve port status, VLAN, MAC table, and traffic statistics with automatic session management and retry functionality.

## Script List

### 1. get_elecom_swhub_info.py
Script to retrieve data directly from the switch

```bash
# Execute with switch-specific .env file (recommended)
python3 get_elecom_swhub_info.py --env-file .env.office-floor1 --mac --pretty
python3 get_elecom_swhub_info.py --env-file .env.datacenter-rack1 --vlan --pretty

# Display switch information summary (recommended)
python3 get_elecom_swhub_info.py --env-file .env.office-floor1 --summary

# Get all port statistics (GE1-GE8 + LAG1-LAG4)
python3 get_elecom_swhub_info.py --env-file .env.office-floor1 --traffic --pretty

# Get all information
python3 get_elecom_swhub_info.py --env-file .env.office-floor1 --all --pretty

# Direct specification via command-line arguments (not recommended: remains in history)
python3 get_elecom_swhub_info.py --ip 192.168.1.1 --user username --password pass --mac --pretty
```

### 2. disconnect_all_sessions.py
Script to disconnect all sessions from the switch

```bash
# Execute with switch-specific .env file (recommended)
python3 disconnect_all_sessions.py --env-file .env.office-floor1
python3 disconnect_all_sessions.py --env-file .env.datacenter-rack1

# Direct specification via command-line arguments (not recommended: remains in history)
python3 disconnect_all_sessions.py --ip 192.168.1.1 --user username --password pass
```

## Options

### get_elecom_swhub_info.py
- `--env-file`: Path to .env file (recommended, default: .env)
- `--ip`: Switch IP address (direct specification, not recommended)
- `--user`: Username (direct specification, not recommended)
- `--password`: Password (direct specification, not recommended)
- `--summary`: Display switch information summary (recommended)
- `--status`: Port status
- `--port`: Port configuration information
- `--vlan`: VLAN information
- `--mac`: MAC address table
- `--traffic`: Traffic statistics (all ports)
- `--main`: Switch basic information
- `--all`: All information
- `--pretty`: Formatted JSON output

### disconnect_all_sessions.py
- `--env-file`: Path to .env file (recommended, default: .env)
- `--ip`: Switch IP address (direct specification, not recommended)
- `--user`: Username (direct specification, not recommended)
- `--password`: Password (direct specification, not recommended)

## Security Notes

### Credential Management

1. **Creating .env files (recommended method)**
   ```bash
   # Copy .env.example to create .env files for each switch
   cp .env.example .env.switch1
   cp .env.example .env.switch2
   
   # Edit each .env file to set actual credentials
   nano .env.switch1
   nano .env.switch2
   
   # Set permissions to 600 (owner read/write only)
   chmod 600 .env.switch*
   ```

2. **.env file content example**
   ```
   SWITCH_IP=192.168.1.1
   SWITCH_USER=your_username
   SWITCH_PASSWORD=your_password
   ```

3. **Managing multiple switches**
   ```bash
   # Create .env files for each switch
   .env.office-floor1    # Office 1st floor switch
   .env.office-floor2    # Office 2nd floor switch
   .env.datacenter-rack1 # Datacenter rack 1 switch
   .env.home-main        # Home main switch
   
   # Specify target switch with --env-file when using
   python3 get_elecom_swhub_info.py --env-file .env.office-floor1 --mac --pretty
   python3 get_elecom_swhub_info.py --env-file .env.datacenter-rack1 --all --pretty
   ```

4. **Important notes**
   - Do not commit .env files to version control systems
   - Do not share credentials with others
   - Change passwords regularly
   - Access only from trusted networks
   - Avoid specifying credentials via command-line arguments (they remain in shell history)
   - Always explicitly specify .env file with `--env-file` option
   - Create and manage separate .env files for each switch

## Available Information

1. **Port Status** (--status)
   - Link state (UP/DOWN)
   - Speed (1G/2.5G)
   - Duplex (Full/Half)

2. **Port Information** (--port)
   - Detailed port configuration
   - Panel layout

3. **VLAN Information** (--vlan)
   - VLAN configuration
   - Port VLAN settings
   - VLAN membership

4. **MAC Address Table** (--mac)
   - Dynamic MAC addresses
   - Static MAC addresses

5. **Traffic Statistics** (--traffic)
   - Statistics for all ports (GE1-GE8 + LAG1-LAG4)
   - Received/transmitted bytes
   - Received/transmitted packets
   - Error counters

6. **Switch Basic Information** (--main)
   - System information
   - Port list
   - Menu structure

## Usage Notes

- There is a limit on concurrent connections to the switch (1 session only)
- If you are logged into the switch via browser, log out before running the script
- When accessing consecutively, wait a few seconds after session disconnection
- If connection errors occur, clear sessions with `disconnect_all_sessions.py`
- Use `--summary` option to quickly check the switch status

## License

MIT License - see [LICENSE](LICENSE) file for details

## Author

Yoichi Takizawa (yo1t)
- GitHub: https://github.com/yo1t/elecom-switch-management
