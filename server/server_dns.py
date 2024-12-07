import time
import os

# update dns filters
def main():
    while(True):
        if os.path.exists("/home/ubuntu/dnsmasq/flag"):   
            os.remove("/home/ubuntu/dnsmasq/flag")
            os.system("cp /home/ubuntu/dnsmasq/* /etc/dnsmasq.d/")
            os.system("systemctl restart dnsmasq")  
        time.sleep(1)

if __name__ == '__main__':
    main()