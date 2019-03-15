import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
plt.figure(figsize=(8,8))

class node(object):
    __slot__=('x','y','energy','broadcast_radius','active_slot','parent','id','updated','broadcast_count','state')
    #threshold distance  m
    thr_distance=87

    #energy of transimitting circuit loss  nJ/bit
    energy_trans=50

    #amp_lification loss for the Free Space Model  pJ/bit/m2
    amp_fs=10*10**(-3)

    #amplification loss for the Multi-path Fading Model  pj/bit/m4
    amp_mpf=0.0013

    #initial energy  J
    E0=0.5*10**(9)
    def __init__(self,x,y,broadcast_radius,active_slot,_id):
        self.x=x
        self.y=y
        self.energy=self.E0
        self.broadcast_radius=broadcast_radius
        self.active_slot=active_slot
        self.id=_id
        self.updated=False
        self.broadcast_count=0
        self.parent=-1
        # -1 means no parent node
        self.state='ready'
        # ready:ready to receve data or transimit data
        # receiving:current time slot is receiving data,therefore unable to broadcast
        # broadcasting:likewise
        
    def broadcast(self,collision,data,network,slot,updated_num):
        for i in collision[self.id]:
            if(network[i].state=='broadcasting'):
                print("collision:node "+str(self.id)+" + node "+str(network[i].id))
                return updated_num
        network[self.id].state='broadcasting'
        print("node "+str(self.id)+" start broadcasting")
        network[self.id].energy-=self.transimit_energy_loss(data)
        network[self.id].broadcast_count+=1;
        for i in reachable[self.id]:
            if(slot in network[i].active_slot and not network[i].updated and network[i].state=='ready'):
                ## simulating the receiving process of nodes
                network[i].updated=True
                network[i].state='receiving'
                updated_num+=1
                print("node "+str(network[i].id)+" start receiving")
                network[i].energy-=self.receive_energy_loss(data)
        network[self.id].state='ready'
        return updated_num
        
    # calculating the energy loss of transimiting (data) bit code
    def transimit_energy_loss(self,data):
        energy_loss=data*self.energy_trans+data*self.amp_fs*self.broadcast_radius**2 if self.broadcast_radius<self.thr_distance else data*self.energy_trans+data*self.amp_mpf*self.broadcast_radius**4
        return energy_loss
        
    # calculating the energy loss of receiving (data) bit code
    def receive_energy_loss(self,data):
        return data*self.energy_trans
        
        
            
        

## parameters

#number of nodes in the natwork
N=100

# working period
T=6

# Duty cycle of the node
D=0.6


# total time slot
total_time=1000

# network range
Xm=25
Ym=25

# fixed broadcast radius
radius=6

# the amount of data to be transmitted (bit)
Data=2048

## global variable

# collision matrix
collision=[set() for i in range(N)]

# record reachable node of i
reachable=[set() for i in range(N)]

plt.rcParams['figure.figsize'] = (16, 16) # 设置figure_size尺寸

## init a network with fixed broadcast radius
def init_network(N):
    network=[]
    theta=np.linspace(0,2*np.pi,800)
    for i in range(N):
        #x=random.uniform(0,Xm)
        #y=random.uniform(0,Ym)
        x,y=network_position[i]
        # plot node
        plt.scatter(x,y,marker=('v' if i==0 else '.'),c=('r' if i==0 else 'g'))
        # plot broadcast range
        plt.plot(x+radius*np.cos(theta),y+radius*np.sin(theta),c=('r' if i==0 else 'g'))
        active_slot=random.sample(range(0,T),round(T*D))
        # using fixed radius
        network.append(node(x,y,radius,active_slot,i))
    # sink node
    #network[0].updated=True
    plt.show()
    return network

# initiate collision matrix
def collision_domain_init(network):
    for i in range(N):
        for j in range(N):
            if(i!=j):
                distance=((network[i].x-network[j].x)**2+(network[i].y-network[j].y)**2)**(1/2)
                if(distance<network[i].broadcast_radius+network[j].broadcast_radius):
                    collision[i].add(j)
                    collision[j].add(i)
                if(distance<network[i].broadcast_radius):
                    reachable[i].add(j)


# change the state of node to "ready"
def renew_state(network):
    for node in network:
        node.state="ready"

# sort the network according to the number of node it covers
def QuickSort(net,firstIndex,lastIndex):
    if firstIndex<lastIndex:
        divIndex=Partition(net,firstIndex,lastIndex)
        QuickSort(net,firstIndex,divIndex)       
        QuickSort(net,divIndex+1,lastIndex)
    else:
        return
 
 
def Partition(net,firstIndex,lastIndex):
    i=firstIndex-1
    for j in range(firstIndex,lastIndex):
        if len(reachable[net[j].id])>=len(reachable[net[lastIndex].id]):
            i=i+1
            net[i],net[j]=net[j],net[i]
    net[i+1],net[lastIndex]=net[lastIndex],net[i+1]
    return i

def sort_network(network):
    sorted_network=[]
    for node in network:
        sorted_network.append(node)
    QuickSort(sorted_network,0,len(sorted_network)-1)
    return sorted_network
    


## sink node start disseminating code
def start_dissenminating(network):
    ## total count of nodes already updated its code
    updated_num=0
    for i in range(total_time):
        time_slot=i%T
        # renew the state of the node
        renew_state(network)
        # sort the network by the number of covered nodes
        #sorted_network=sort_network(network)
        for node in network:
            if(node.id==0 and i<T):
                # sink node broadcast |T| times to ensure nodes near sink can receive the code
                updated_num=node.broadcast(collision,Data,network,time_slot,updated_num)
            if(node.id>0 and node.updated==True and node.state=='ready' and time_slot in node.active_slot):
                # not sink node, and it has the updated code, and it is neither broadcasting nor receiving code
                # then broadcast code to the reachable nodes near it
                updated_num=node.broadcast(collision,Data,network,time_slot,updated_num)
            
            ## whether all the nodes in the network had updated their code
            if(updated_num==N):
                print("Done dissenminating code!")
                return updated_num,i
    print("Terminated.")
    return updated_num,total_time
                    

## calculate the total energy lost of one dissenmination
def energy_loss(network):
    energy_loss=0
    broadcast_count=0
    for node in network:
        energy_loss+=node.E0-node.energy
        broadcast_count+=node.broadcast_count
    return energy_loss*10**(-6),broadcast_count

# display the energy heatmap

def display_energy_consume_heatmap(network):
    x=[]
    y=[]
    z=[]
    for node in network:
        x.append(node.x)
        y.append(node.y)
        z.append(node.E0-node.energy)
        df=pd.DataFrame({
                "x":x,
                "y":y,
                "z":z
        })
    df.plot.hexbin(x='x',y='y',C='z',gridsize=10)

        
def run_sim(n):
    # simulate n time and get the mean energy comsumption and broadcasts count
    time=[]
    energy=[]
    broadcast=[]
    completed_count=0
    for i in range(0,n):
        network=init_network(N)
        collision_domain_init(network)
        updated_num,time_used=start_dissenminating(network)
        if(updated_num==N):
            # if the simulation completed code dissenmination(every node had been updated)
            completed_count+=1
            time.append(time_used)
            energy_los,broadcast_count=energy_loss(network)
            energy.append(energy_los)
            broadcast.append(broadcast_count)
    mean_time="{:.3f}".format(sum(time)/len(time))
    mean_energy_comsume="{:.3f}".format(sum(energy)/len(energy))
    mean_broadcast="{:.3f}".format(sum(broadcast)/len(broadcast))
    print(str(completed_count)+" times completed in "+str(n)+" times simulation")
    print("Average time used:"+str(mean_time))
    print("Average energy consumption:"+str(mean_energy_comsume))
    print("Average broadcasts count:"+str(mean_broadcast))
            



 

