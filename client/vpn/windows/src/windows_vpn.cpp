#include "pch.h"
#include "windows_vpn.h"

static int get_conn_by_name(char* name, HRASCONN &handle) {
    // Get size needed for connection buffer
    DWORD size = 0;
    DWORD num_con = 0;
    DWORD result = RasEnumConnectionsA(NULL, &size, &num_con);
    if (result == ERROR_SUCCESS){
        handle = nullptr;
        return 0;
    }
    if (result != ERROR_BUFFER_TOO_SMALL) {
        std::cerr << "Failed to retrieve buffer size. Error: " << result << std::endl;
        return 1;
    }
    if (size % sizeof(RASCONNA) != 0) {
        std::cerr << "Unexpected size alignment!" << std::endl;
        return 1;
    }

    // Init buffer
    LPRASCONNA connections = new RASCONNA[size / sizeof(RASCONNA)];
    ZeroMemory(connections, size);
    connections[0].dwSize = sizeof(RASCONNA);

    // Get Connections
    result = RasEnumConnectionsA(connections, &size, &num_con);
    if (result != ERROR_SUCCESS) {
        std::cerr << "Failed to retrieve connections. Error: " << result << std::endl;
        return 1;
    }

    for (DWORD i = 0; i < num_con; i++) {
        if (strcmp(connections[i].szEntryName, name) == 0) {
            handle = connections[i].hrasconn;
            break;
        }
    }

    delete[] connections;
    return 0;
}

int create_profile(char* vpnEntryName, char* vpnServerAddress, char* pbkPath) {
    DWORD result = 0;
    
    // Initialize the RASENTRY struct
    RASENTRYA rasEntry;
    ZeroMemory(&rasEntry, sizeof(RASENTRYA));
    rasEntry.dwSize = sizeof(RASENTRYA);
    rasEntry.dwfOptions = RASEO_RemoteDefaultGateway | 
                          RASEO_RequireDataEncryption | 
                          RASEO_RequireEAP | 
                          RASEO_ShowDialingProgress | 
                          RASEO_PreviewDomain | 
                          RASEO_PreviewUserPw;
    strcpy_s(rasEntry.szLocalPhoneNumber, vpnServerAddress);
    rasEntry.dwfNetProtocols = RASNP_Ip;
    strcpy_s(rasEntry.szDeviceType, "RASDT_Vpn");
    strcpy_s(rasEntry.szDeviceName, "WAN Miniport (IKEv2)");
    //rasEntry.dwIdleDisconnectSeconds = RASIDS_UseGlobalValue;
    rasEntry.dwType = RASET_Vpn;
    //rasEntry.dwEncryptionType = ET_Require; //seems redundant
    //rasEntry.dwCustomAuthKey = 25;
    rasEntry.dwVpnStrategy = VS_Ikev2Only;
    rasEntry.dwfOptions2 = RASEO2_DontNegotiateMultilink | RASEO2_ReconnectIfDropped | RASEO2_IPv6RemoteDefaultGateway | RASEO2_DontUseRasCredentials | ET_RequireMax;
    rasEntry.dwRedialCount = 3;
    rasEntry.dwRedialPause = 30;

    // Create profile
    result = RasSetEntryPropertiesA(
        pbkPath,
        vpnEntryName,
        &rasEntry,
        sizeof(rasEntry),
        NULL,
        0
    );
    // Check for errors
    if (result != ERROR_SUCCESS) {
        std::cerr << "Error creating VPN entry: " << result << std::endl;
        return 1;
    }

    // EAP Data for MSCHAPv2
    unsigned char eapData[256];
    ZeroMemory(eapData, sizeof(eapData));

    // Set the EAP user data
    DWORD dwResult = RasSetEapUserDataA(NULL, pbkPath, vpnEntryName, eapData, 256);

    if (dwResult != ERROR_SUCCESS) {
        char errorMessage[512];
        RasGetErrorStringA(dwResult, errorMessage, 512);
        std::cout << "Failed to set EAP credentials: " << errorMessage << std::endl;
    }

    return 0;
}

int delete_profile() {
    //Not really needed as the profile is stored in a seperate pbk
    return 0;
}

int connect_vpn(char* profileName, char* username, char* password, char* pbkPath) {
    RASDIALPARAMSA param;
    ZeroMemory(&param, sizeof(RASDIALPARAMSA));
    param.dwSize = sizeof(RASDIALPARAMSA);
    strcpy_s(param.szEntryName, profileName);
    BOOL ispw = false;
    DWORD result = RasGetEntryDialParamsA(pbkPath, &param, &ispw);
    if (result != ERROR_SUCCESS) {
        std::cerr << "Error reading parameters. Error: " << result << std::endl;
    }

    strcpy_s(param.szUserName, username);
    strcpy_s(param.szPassword, password);

    HRASCONN hRasConn = NULL;
    result = RasDialA(NULL, pbkPath, &param, 0, NULL, &hRasConn);

    // Check for connection errors
    if (result != ERROR_SUCCESS) {
        std::cerr << "Error connecting to VPN: " << result << std::endl;
        return 1;
    }

    if (!hRasConn) {
        std::cerr << "Error connection handle" << std::endl;
        return 1;
    }

    return 0;
}

int disconnect_vpn(char* profileName) {

    HRASCONN connection;
    DWORD result = get_conn_by_name(profileName, connection);
    if (result != 0 || connection == nullptr) {
        std::cerr << "Failed find profile. Error:" << result << std::endl;
        return 1;
    }

    result = RasHangUpA(connection);
    if (result != ERROR_SUCCESS) {
        std::cerr << "Failed to disconnect. Error:" << result << std::endl;
        return 1;
    }

    return 0;
}

int status(char* profileName) {
    HRASCONN connection;
    DWORD result = get_conn_by_name(profileName, connection);
    if (result != 0 ) {
        std::cerr << "Failed find profile. Error:" << result << std::endl;
        return -1;
    }

    RASCONNSTATUSA status;
    ZeroMemory(&status, sizeof(RASCONNSTATUSA));
    status.dwSize = sizeof(RASCONNSTATUSA);
    result = RasGetConnectStatusA(connection, &status);
    if (result != ERROR_SUCCESS) {
        std::cerr << "Failed to get connection status. Error: " << result << std::endl;
        return -1;
    }

    if (status.rasconnstate == RASCS_Connected) {
        return 0;
    }
    return 1;
}

