#include <linux/kernel.h>          // Kernel header
#include <linux/module.h>          // Required for all kernel modules
#include <linux/netfilter.h>       // Netfilter header
#include <linux/netfilter_ipv4.h>  // IPv4-specific Netfilter header
#include <linux/ip.h>              // IP header structures
#include <linux/init.h>            // Required for module init/exit macros
#include <linux/net.h>             // For network-related structures

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Ted Nowicki");
MODULE_DESCRIPTION("A simple packet interceptor");
MODULE_VERSION("0.1");

// Use to register netfilter hook
static struct nf_hook_ops nfho;

// The hook function that will be called for every packet
unsigned int hook_func(void *priv,
                       struct sk_buff *skb,
                       const struct nf_hook_state *state) {
    //Pointer to ip header
    struct iphdr *ip_header;

    // Check if the socket buffer is NULL
    if (!skb) {
        return NF_ACCEPT;
    }
    //Ensure skb is an IP packet-uneeded: hook proto is INET
    if (skb->protocol != htons(ETH_P_IP)) {
	return NF_ACCEPT;
    }

    // Extract the IP header from the socket buffer
    ip_header = ip_hdr(skb);
    if (ip_header) { 
        // Log the source and destination IP addresses to the kernel log
        printk(KERN_INFO "Packet intercepted: Source IP: %pI4, Dest IP: %pI4\n",
               &ip_header->saddr, &ip_header->daddr);
    }

    return NF_ACCEPT; 
}

//Module init function
static int __init packet_interceptor_init(void) {
    // Set up the Netfilter hook options
    //set hook function
    nfho.hook = hook_func;
    //netfilter hook type NF_INET_FORWARD
    nfho.hooknum = NF_INET_PRE_ROUTING; 
    //Protocol Family
    nfho.pf = PF_INET;
    //highest priority    
    nfho.priority = NF_IP_PRI_FIRST;    

    // Register the hook with the Netfilter subsystem
    nf_register_net_hook(&init_net, &nfho);
    printk(KERN_INFO "Packet interceptor loaded\n");
    return 0;
}

//Module exit function
static void __exit packet_interceptor_exit(void) {
    // Unregister the nethook
    nf_unregister_net_hook(&init_net, &nfho);
    printk(KERN_INFO "Packet interceptor unloaded\n");
}

//entry point of the module
module_init(packet_interceptor_init); 
//exit point of the module
module_exit(packet_interceptor_exit);

