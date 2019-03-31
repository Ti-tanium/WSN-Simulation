import random
import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
plt.figure(figsize=(8,8))

class node(object):
    __slot__=('x','y','energy','broadcast_radius','active_slot','parent','id','updated','broadcast_count','state','priority','layer')
    
    # effective data receive/forward speed  bps
    speed=16*1024*1024
    
    # Power Consumption of receive  mW
    receive_consumption=303.6
    
    # Power Consumption of transimit mW
    transimit_consumption=617.1
    
    # Power Consumption of idle mW
    idle_consumption=230
    
    # start up energy  mj
    # igore the start up energy for now
    start_up_energy=299
    
    # the duration of time slot  s
    duration=0.1
    
    #initial energy  mJ
    E0=10**(3)
    
    
    ## First Order Radio Model
    # energy disspation of radio  j/bit
    E_elec=50*10**(-9)
    
    # transmit amplifier   j/bit/m2
    E_amp=100*10**(-12)
    
    # power consumption in idle state   W
    P_idle=1.15
    
    #
    
    def __init__(self,x,y,broadcast_radius,active_slot,_id):
        self.x=x
        self.y=y
        self.energy=self.E0
        self.broadcast_radius=broadcast_radius
        self.active_slot=active_slot
        self.id=_id
        self.updated=False
        self.broadcast_count=0
        self.parent=-1  # -1 means no parent node
        self.state='ready'
        self.priority=0
        self.layer=0
        # ready:ready to receve data or transimit data
        # receiving:current time slot is receiving data,therefore unable to broadcast
        # broadcasting:likewise
        
    def broadcast(self,collision,data,network,slot,updated_num):
        for i in collision[self.id]:
            if(network[i].state=='broadcasting'):
                print("collision:node "+str(self.id)+" + node "+str(network[i].id))
                return updated_num
        network[self.id].state='broadcasting'
        #print("node "+str(self.id)+" start broadcasting")
        network[self.id].energy-=self.transimit_energy_loss(data)
        network[self.id].broadcast_count+=1;
        for i in reachable[self.id]:
            if(slot in network[i].active_slot and not network[i].updated and network[i].state=='ready'):
                ## simulating the receiving process of nodes
                network[i].updated=True
                network[i].state='receiving'
                updated_num+=1
                #print("node "+str(network[i].id)+" start receiving")
                network[i].energy-=self.receive_energy_loss(data)
        network[self.id].state='ready'
        return updated_num
        
    # calculating the energy loss of transimiting (data) bit code
    def transimit_energy_loss(self,data):
#        time=data/self.speed
#        return time*self.transimit_consumption
        # first order radio model
        return data*self.E_elec+data*self.broadcast_radius**(2)*self.E_amp
        
    # calculating the energy loss of receiving (data) bit code
    def receive_energy_loss(self,data):
#        time=data/self.speed
#        return time*self.receive_consumption
        # first order radio model
        return data*self.E_elec
    
    # simulate idle state
    def idle_energy_loss(self):
#        self.energy-self.duration*self.idle_consumption
        self.energy-self.duration*self.P_idle
        

## parameters

#number of nodes in the natwork
N=500

# working period
T=6

# Duty cycle of the node
D=1/6


# total time slot
total_time=100

# network range
Xm=1000
Ym=1000

# fixed broadcast radius
radius=80

# the amount of data to be transmitted (bit)
Data=1024*1024*1

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
#        x=random.uniform(0,Xm)
#        y=random.uniform(0,Ym)
        x,y=network_position_500[i]
        # plot node
        #plt.scatter(x,y,marker=('v' if i==0 else '.'),c=('r' if i==0 else 'g'))
        # plot broadcast range
        #plt.plot(x+radius*np.cos(theta),y+radius*np.sin(theta),c=('r' if i==0 else 'g'))
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
# refresh the network for another simulation
def refresh_network(network):
    for i in range(0,N):
        network[i].state="ready"
        network[i].energy=network[i].E0
        network[i].updated=False
        network[i].broadcast_count=0
        network[i].parent=-1

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
        if net[j].priority>=net[lastIndex].priority:
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

## calculate priority by counting the number of unupdated code in reachable range
def cal_prior(network):
    for node in network:
        n=0
        for i in reachable[node.id]:
            if(network[i].updated==False):
                n+=1
        network[node.id].priority=n

def neighbor():
    neighbor_count=[]
    for i in range(N):
        neighbor_count.append(len(reachable[i]))
    return neighbor_count

def distance_cal(network):
    distance=[0 for i in range(N)]
    for i in range(N):
        Dsi=((network[i].x-network[0].x)**2+(network[i].y-network[0].y)**2)**0.5
        distance[network[i].id]=Dsi
    return distance

# adaptive duty cycle
def adapt_dutyCycle1(network):
    # mean_neighbor,max_neighbor=neighbor()
    distance=distance_cal(network)
    mean_distance=sum(distance)/N
    max_distance=max(distance)
    for i in range(0,N):
        # clear duty cycle
        network[i].active_slot.clear()
        # calculate adaptive duty cycle
        duty_cycle=network[i].energy/network[i].E0
        network[i].active_slot=random.sample(range(0,T),round(T*duty_cycle))
        
def adapt_dutyCycle4(network):
    distance=distance_cal(network)
    mean_distance=sum(distance)/N
    max_distance=max(distance)
    neighbor_count=neighbor();
    for i in range(0,N):
        # clear duty cycle
        network[i].active_slot.clear()
#         calculate adaptive duty cycle
        Ck=network[i].energy/network[i].E0 if distance[i]>=mean_distance else neighbor_count[i]/max(neighbor_count)
        duty_cycle=1/T+Ck*(1-1/T)
        network[i].active_slot=random.sample(range(0,T),round(T*duty_cycle))
    

# adaptive broadcast radius
def adapt_radius(network):
    # skip sink node (node.id=0)
    distance=distance_cal(network)
    mean_distance=sum(distance)/N
    max_distance=max(distance)
    for i in range(1,N):
        Ck=network[i].energy/network[i].E0 if distance[i]>=mean_distance else distance[i]/max_distance
        network[i].broadcast_radius=90+Ck*(Xm-90)
## sink node start disseminating code
def start_dissenminating(network,density_first,adaptive_duty_cycle,adaptive_radius):
    ## total count of nodes already updated its code
    updated_num=0
    for i in range(total_time):
        time_slot=i%T
        # renew the state of the node
        renew_state(network)
        cal_prior(network)

        # sort the network by the number of unupdated covered nodes
        if(density_first):
            sorted_network=sort_network(network)
        else:
            sorted_network=network
        
        #whether use adaptive duty cycle scheme
        if(adaptive_duty_cycle):
            adapt_dutyCycle1(network)
        
        #whether use adaptive braodcast radius scheme
        if(adaptive_radius):
            adapt_radius(network)
        
        for node in sorted_network:
            
            if(node.priority==0):
                # if every sensor node in node's coverage has been updated,then skip this node
                continue
            if(node.id==0 and i<T):
                # sink node broadcast |T| times to ensure nodes near sink can receive the code
                updated_num=node.broadcast(collision,Data,network,time_slot,updated_num)
            if(node.id>0 and node.updated==True and node.state=='ready' and time_slot in node.active_slot):
                # not sink node, and it has the updated code, and it is neither broadcasting nor receiving code
                # then broadcast code to the reachable nodes near it
                updated_num=node.broadcast(collision,Data,network,time_slot,updated_num)
            
            if(time_slot in node.active_slot and node.updated==False and node.state=="ready"):
                # node is active but don't have data to broadcast neither is receiving data
                node.idle_energy_loss()
            
            ## whether all the nodes in the network had updated their code
            if(updated_num==N):
                print("Done dissenminating code!")
                return updated_num,i
    print("Terminated.")
    return updated_num,total_time
                    

## calculate the total energy lost of one dissenmination
def evaluate(network):
    energy_loss=0    # mj
    broadcast_count=0
    for node in network:
        energy_loss+=node.E0-node.energy
        broadcast_count+=node.broadcast_count
    return energy_loss,broadcast_count

# display the energy heatmap
def display_energy_residual_heatmap(network,z):
    x=[]
    y=[]
    for node in network:
        x.append(node.x)
        y.append(node.y)
    df=pd.DataFrame({
            "x":x,
            "y":y,
            "z":z
    })
    df.plot.hexbin(x='x',y='y',C='z',gridsize=10,figsize=(10,8))
    
# display node distribution and radius
def display_net(network):
    theta=np.linspace(0,2*np.pi,800)
    fig,ax=plt.subplots(figsize=(12,12))

    for node in network:
        # plot node
        ax.scatter(node.x,node.y,linewidths=8,marker=('v' if node.id==0 else '.'),c=('r' if node.id==0 else 'g'))
        # plot broadcast range
        plt.plot(node.x+radius*np.cos(theta),node.y+radius*np.sin(theta),c=('r' if node.id==0 else 'g'))
    fig.show()
        
    
network=init_network(N)

def run_sim(n,density_first=False,adaptive_duty_cycle=False,adaptive_radius=False,ABRCD=False):
    # simulate n time and get the mean energy comsumption and broadcasts count
    time=[]
    energy=[]
    broadcast=[]
    completed_count=0
    energy_remain=[set() for i in range(0,N)]
    #network=init_network(N)
    #using ABRCD scheme to adapt radius acording to the distance between node i and sink
    if(ABRCD):
        #ABRCD scheme parameters
        q=1.2
        r=80
        for i in range(1,N):
            distance=((network[0].x-network[i].x)**2+(network[0].y-network[i].y)**2)**(1/2)
            layer=math.ceil(math.log(1+distance*(q-1)/r,q))
            network[i].layer=layer
            network[i].broadcast_radius=r*q**(layer-1)
    #display_net(network)
    collision_domain_init(network)
    for i in range(0,n):
        # after a simulation, the network is changed
        # so it needs to be refresh for another simulation
        refresh_network(network)
        updated_num,time_used=start_dissenminating(network,density_first,adaptive_duty_cycle,adaptive_radius)
#
        if(updated_num==N):
            completed_count+=1        
        for node in network:
            energy_remain[node.id].add(node.energy)
        time.append(time_used)
        energy_los,broadcast_count=evaluate(network)
        energy.append(energy_los)
        broadcast.append(broadcast_count)
    ## calculate the average energy left for each node and draw heat map
    mean_energy_remain=[0 for i in range(0,N)]
    for i in range(0,N):
        mean_energy_remain[i]=sum(energy_remain[i])/len(energy_remain[i]) if len(energy_remain[i]) !=0 else 0
    display_energy_residual_heatmap(network,mean_energy_remain)
    # variance of energy consumptions
    variance=0
    average=sum(mean_energy_remain)/len(mean_energy_remain)
    for i in range(N):
        variance+=(mean_energy_remain[i]-average)**2/N
    #average time used to dissenminatie data
    mean_time="{:.3f}".format(sum(time)*network[0].duration/len(time)) if len(time)!=0 else 0
    # avaerage total energy comsumed
    mean_energy_consumption="{:.3f}".format(sum(energy)/len(energy)) if len(energy)!=0 else 0
    # average broadcast count
    mean_broadcast = "{:.3f}".format(sum(broadcast)/len(broadcast)) if len(broadcast)!=0 else 0

    print(str(completed_count)+" times completed in "+str(n)+" times simulation")
    print("Net configuration:"+"N="+str(N)+" T="+str(T)+" D="+str("{:.3f}".format(D))+" r="+str(radius))
    print("Scheme:"," ABRCD" if ABRCD else ""," Adaptive Radius" if adaptive_radius else ""," Adaptive Duty Cycle" if adaptive_duty_cycle else "")
    print("Average Broadcast Delay(s):"+str(mean_time))
    print("Average Total Energy consumption:"+str(mean_energy_consumption))
    print("Average broadcasts count:"+str(mean_broadcast))
    print("Standard Deviation of energy remain:"+str(variance**(0.5)))
            