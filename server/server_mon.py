import time
import os

# terminate server after 15 minutes of inactivity 

# Return true if there is an active VPN connection
def check_connection():
    try:
        result = os.system('swanctl -l | grep -o "ESTABLISHED" | wc -l')
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
    duration = 15
    count = freq * duration
    while(True):
        if check_connection():
            # Reset
            count = freq * duration
        else:
            count -= 1
        if count < 0:
            os.system("shutdown now -P")
        time.sleep(60//freq)

if __name__ == '__main__':
    main()