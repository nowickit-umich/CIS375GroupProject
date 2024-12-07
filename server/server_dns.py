import time
import os

# update dns filters
def main():
    while(True):
        if not os.path.isfile("/home/ubuntu/dnsmasq/flag"):
            time.sleep(1)
        os.remove("/home/ubuntu/dnsmasq/flag")
        os.system("cp /home/ubuntu/dnsmasq/* /etc/dnsmasq.d/")
        os.system("systemctl reload dnsmasq")  

if __name__ == '__main__':
    main()