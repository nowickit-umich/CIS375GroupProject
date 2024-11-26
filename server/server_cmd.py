import time
import os
import subprocess

# terminate server after 15 minutes of inactivity 

# Return true if there is an active VPN connection
def check_connection():
    try:
        result = os.system('sudo swanctl -l | grep -o "ESTABLISHED" | wc -l')
        if result != 0:
            return True
    except:
        return False
    return False

# monitor
def main():
    # Frequency of checks in checks/minute
    freq = 2
    # Number of minutes before shutdown
    time = 15
    count = freq * time
    while(True):
        if check_connection:
            # Reset
            count = freq * time
        else:
            count -= 1
        if count < 0:
            os.system("sudo shutdown now -P")
        time.sleep(60//freq)

if __name__ == '__main__':
    main()