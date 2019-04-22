import random
import numpy as np
import pandas as pd
import math
import copy
import matplotlib.pyplot as plt
plt.figure(figsize=(8,8))

## parameters

#number of nodes in the natwork
N=500

# working period
T=6

# Duty cycle of the node
D=1/6

# thresh for adding time slot
nthresh=4

# total time slot
total_time=200

# network range
Xrange=1000
Yrange=1000

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


class node(object):
    __slot__=('x','y','energy','broadcast_radius','active_slot','parent','id','updated','broadcast_count','state','priority','layer','priority2','addedActiveSlot','Broadcasted','additionalCoverageArea')
    
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
        self.priority2=0
        self.layer=0
        self.addedActiveSlot=set()
        self.Broadcasted="no"
        self.additionalCoverageArea=0
        # ready:ready to receve data or transimit data
        # receiving:current time slot is receiving data,therefore unable to broadcast
        # broadcasting:likewise
        
    def broadcast(self,collision,data,network,slot,updated_num):
        for i in collision[self.id]:
            if(network[i].state=='broadcasting'):
#                print("collision:node "+str(self.id)+" + node "+str(network[i].id))
                return updated_num
        network[self.id].state='broadcasting'
#        print("node "+str(self.id)+" start broadcasting")
        network[self.id].energy-=self.transimit_energy_loss(data)
        network[self.id].broadcast_count+=1;
        if(slot in network[self.id].addedActiveSlot):
            network[self.id].addedActiveSlot.remove(slot)
            if(len(network[self.id].addedActiveSlot)==0):
                network[self.id].Broadcasted="Yes"
        for i in reachable[self.id]:
            if(slot in network[i].active_slot|network[i].addedActiveSlot and not network[i].updated and network[i].state=='ready'):
                ## simulating the receiving process of nodes
                network[i].updated=True
                network[i].state='receiving'
                updated_num+=1
                # remove receive slot
                if(slot in network[i].addedActiveSlot):
                    network[i].addedActiveSlot.remove(slot)
#                print("node "+str(network[i].id)+" start receiving")
                network[i].energy-=self.receive_energy_loss(data)
        #network[self.id].state='ready'
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
        

## init a network with fixed broadcast radius
def init_network(N):
    network=[]
    theta=np.linspace(0,2*np.pi,800)
    for i in range(N):
#        x=random.uniform(0,Xrange)
#        y=random.uniform(0,Yrange)
        x,y=network_position_500[i]
        # plot node
        #plt.scatter(x,y,marker=('v' if i==0 else '.'),c=('r' if i==0 else 'g'))
        # plot broadcast range
        #plt.plot(x+radius*np.cos(theta),y+radius*np.sin(theta),c=('r' if i==0 else 'g'))
        active_slot=set(random.sample(range(T),round(T*D)))
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
        network[i].addedActiveSlot=set()
        network[i].Broadcasted="no"
        network[i].additionalCoverageArea=0
        
## select a list of nodes to broadcast (Greedy approach)
def selectBroadcastNodes(network,nthresh,time_slot):    
    networkCopy=copyNetwork(network)
    selected1=[] # first round selection
    selected2=[] # second round selection
    for node in networkCopy:
        if(node.updated==False):
            # skip unupdated nodes
            continue
        if(node.state!="ready"):
            continue
            
        num1=0 # denote the number of coverd unupdated nodes
        num2=0 # denote the number of coverd unupdated nodes that activate at the same time slot as the broadcast node
        for i in reachable[node.id]:
            if(network[i].updated==False):
                num1+=1
                if(len(node.active_slot & network[i].active_slot)>0):
                    num2+=1

        node.priority=num1
        node.priority2=num2
        selected1.append(copy.copy(node))
    
    # key for sorting
    def sortBynum1(elem):
        return elem.priority
    def sortBynum2(elem):
        return elem.priority2
    
    # sort by num1
    selected1.sort(key=sortBynum1,reverse=True)
    # sort by num2
    #selected1.sort(key=sortBynum2,reverse=True)

    active={}
    active_record=[{'count':0,'set':set()} for i in range(T)]
## sort by num1   
    for node in selected1:
        if(node.priority==0):
            continue
        n=0
        for i in reachable[node.id]:
            if(networkCopy[i].updated==False):
               n+=1
               if(len(node.active_slot & network[i].active_slot)==0):
                    for j in networkCopy[i].active_slot:
                        active_record[j]['count']+=1
                        active_record[j]['set'].add(i)
               networkCopy[i].updated=True # mark as updated
               
        active[node.id]=active_record
        node.priority=n
        selected2.append(copy.copy(node))
        # add time slot
        for i,slot in enumerate(active[node.id]):
            if(i in node.active_slot or slot['count']==0):
                continue;
            if(slot['count']>=nthresh):
                # if count bigger than thresh, add time slot to broadcast node
                network[node.id].addedActiveSlot.add(i)
            else:
                # add slot to receive node
                for receiveNodeId in slot['set']:
                    ## add the nearest active slot to the current slot
                    addedslot=min(node.active_slot)
                    for j in node.active_slot:
                        if(j>=time_slot):
                            addedslot=j
                    network[receiveNodeId].addedActiveSlot.add(addedslot)   
    return selected2
    
## Select broadcast node by additional coverage area
def ACASelect(network,nthresh,time_slot):    
    networkCopy=copyNetwork(network)
    selected1=[] # first round selection
    selected2=[] # second round selection
    for node in networkCopy:
        if(node.updated==False):
            # skip unupdated nodes
            continue
        if(node.state!="ready"):
            continue
            
        additionalCoverageArea=0
        XM=math.ceil((node.x+node.broadcast_radius)*1)
        Xm=math.ceil((node.x-node.broadcast_radius)*1)
        YM=math.ceil((node.y+node.broadcast_radius)*1)
        Ym=math.ceil((node.y-node.broadcast_radius)*1)
        Xm=Xm if Xm>=0 else 0
        Ym=Ym if Ym>=0 else 0
        XM=XM if XM<=Xrange-1 else Xrange-1
        YM=YM if YM<=Yrange-1 else Yrange-1
        for x in range(Xm,XM+1):
            for y in range(Ym,YM+1):
                distance=((node.x-x/1)**2+(node.y-y/1)**2)**(1/2)
                if(distance<node.broadcast_radius and area[x][y]==0):
                    area[x][y]=1
                    additionalCoverageArea+=1
        node.ACA=additionalCoverageArea
        selected1.append(copy.copy(node))
            
    def sortByAC(elem):
        return elem.additionalCoverageArea
    selected1.sort(key=sortByAC,reverse=True)

    return selected1

    


def distance_cal(network):
    distance=[0 for i in range(N)]
    for i in range(N):
        Dsi=((network[i].x-network[0].x)**2+(network[i].y-network[0].y)**2)**0.5
        distance[network[i].id]=Dsi
    return distance
  

def copyNetwork(network):
    netCopy=[]
    for node in network:
        netCopy.append(copy.copy(node))
    return netCopy


## To make sure the disseminating process goes on, when sensor nodes
## received a packet, it broadcasts in all timeslot in one working cycle.
## the following funciton adds active slot to nodes that is about to broadcast.
def temporaryActive(network):
    selectedNodes=[]
    for node in network:    
        if(node.updated==True and node.state=="ready" and node.Broadcasted=="no"):
            ## active all the time to broadcast to all the surrounding node
            ## just to make sure every node receive the packet
            ## The added active slot will be removed when renew_slot(network)
            ## is called upon.
            node.addedActiveSlot=node.addedActiveSlot.union(set(range(T)))
            node.Broadcasted="ing" 
        n=0
        for i in reachable[node.id]:
            if(network[i].updated==False and node.updated==True):
                n+=1
        node.priority=n
        if(node.priority==0):
            continue
        selectedNodes.append(node);
    return selectedNodes

## sink node start disseminating code
def start_dissenminating(network,greedy,adaptive_duty_cycle,adaptive_radius,AC):
    ## total count of nodes already updated its code
    updated_num=1
    network[0].updated=True
    for i in range(total_time):
    network[0].addedActiveSlot=set(range(T))
        time_slot=i%T
        # renew the state of the node
        renew_state(network)
        #whether use adaptive braodcast radius scheme
        if(adaptive_radius):
            adapt_radius(network)
        
        if(greedy):
            selectedNodes=selectBroadcastNodes(network,nthresh,time_slot)  
        elif(AC):
            selectedNodes=ACASelect(network,nthresh,time_slot)
        else:
            selectedNodes=temporaryActive(network)
            
#        print("Time slot:",time_slot,"len:",len(selectedNodes))
        for node in selectedNodes:
            if(len(node.addedActiveSlot)):
                print("node:",node.id,"slot:",node.addedActiveSlot)
            if(node.state=="ready" and (time_slot in network[node.id].active_slot|network[node.id].addedActiveSlot) and network[node.id].state=="ready" and network[node.id].Broadcasted!="Yes" and network[node.id].updated==True):
                # not sink node, and it has the updated code, and it is neither broadcasting nor receiving code
                # then broadcast code to the reachable nodes near it
                updated_num=network[node.id].broadcast(collision,Data,network,time_slot,updated_num)
            
        
        for node in network:
            if((time_slot in network[node.id].active_slot|network[node.id].addedActiveSlot) and network[node.id].state=="ready"):
                # node is active but don't have data to broadcast neither is receiving data
                network[node.id].idle_energy_loss()
            
        ## whether all the nodes in the network had updated their code
        if(updated_num==N):
            print("Done dissenminating code!")
            return updated_num,i
        
            
    print("Terminated:",updated_num)
    return updated_num,i
                    
## check whether it is possible to complete disseminating code.
## whethear the network is fully connected.
def checkConnection(network):
    copy=copyNetwork(network)
    refresh_network(copy)
    num=1;
    copy[0].Broadcasted=True
    nodes=[copy[0]]
    while(len(nodes)!=0):
        node=nodes.pop();
        for i in reachable[node.id]:
            if(copy[i].Broadcasted==False):
                copy[i].Broadcasted=True
                nodes.append(copy[i])
                num+=1
    if(num==N):
        return True,num
    else:
        return False,num

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

def countUnupdatedNode(network):
    n=0
    for node in network:
        if(node.updated==False):
            n+=1
    return n
    
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

def run_sim(n,greedy=False,adaptive_duty_cycle=False,adaptive_radius=False,ABRCD=False,AC=False):
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
        q=1.5
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
        updated_num,time_used=start_dissenminating(network,greedy,adaptive_duty_cycle,adaptive_radius,L)

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
#    display_energy_residual_heatmap(network,mean_energy_remain)
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
    print("Scheme:"," ABRCD:"+"q="+str(q)+" r0="+str(r) if ABRCD else ""," Adaptive Radius" if adaptive_radius else ""," Adaptive Duty Cycle" if adaptive_duty_cycle else ""," Greedy" if greedy else "")
    print("Average Broadcast Delay(s):"+str(mean_time))
    print("Average Total Energy consumption:"+str(mean_energy_consumption))
    print("Average broadcasts count:"+str(mean_broadcast))
    print("Standard Deviation of energy remain:"+str(variance**(0.5)))

run_sim(1,AC=True)
#q=1.2
#20 times completed in 20 times simulation
#Net configuration:N=500 T=6 D=0.167 r=80
#Scheme:  ABRCD    Greedy
#Average Broadcast Delay(s):1.900
#Average Total Energy consumption:8703.832
#Average broadcasts count:1764.000
#Standard Deviation of energy remain:89.66071976570241

#20 times completed in 20 times simulation
#Net configuration:N=500 T=6 D=0.167 r=80
#Scheme:  ABRCD:q=1.3 r0=80    Greedy
#Average Broadcast Delay(s):1.600
#Average Total Energy consumption:15706.411
#Average broadcasts count:1716.000
#Standard Deviation of energy remain:264.65754324816135

#20 times completed in 20 times simulation
#Net configuration:N=500 T=6 D=0.167 r=80
#Scheme:  ABRCD:q=1.4 r0=80    Greedy
#Average Broadcast Delay(s):1.700
#Average Total Energy consumption:21866.127
#Average broadcasts count:1687.000
#Standard Deviation of energy remain:308.18367446252597

#20 times completed in 20 times simulation
#Net configuration:N=500 T=6 D=0.167 r=80
#Scheme:  ABRCD:q=1.5 r0=80    Greedy
#Average Broadcast Delay(s):1.400
#Average Total Energy consumption:36695.320
#Average broadcasts count:1671.000
#Standard Deviation of energy remain:614.3825767310414

#20 times completed in 20 times simulation
#Net configuration:N=500 T=6 D=0.167 r=80
#Scheme:     Greedy
#Average Broadcast Delay(s):5.000
#Average Total Energy consumption:1238.777
#Average broadcasts count:1676.000
#Standard Deviation of energy remain:4.273786991032401