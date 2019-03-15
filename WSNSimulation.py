import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
plt.figure(figsize=(8,8))

network_position=[(19.249847386239587, 10.774198448728278), (7.751670426888413, 21.240572806696957), (22.70853025682624, 23.13264102906356), (9.576802452896398, 23.737561422858196), (21.38402031735747, 11.809620782720408), (6.132498596605424, 22.628423784600542), (22.103452610469727, 2.54775639291156), (21.51419999436147, 7.8023876970322315), (1.869306537393764, 19.853691301573985), (24.123176431536994, 22.099825871050697), (9.272930071059072, 18.852116730730934), (20.143932789513272, 23.80445772495939), (10.247477520378123, 6.484549425473752), (12.659611728413228, 8.464408131581527), (20.191462437443246, 15.992092314096526), (0.7826676887691092, 8.265903510343154), (6.029660142770371, 0.9361014778996368), (9.64476607209089, 6.7212137626579045), (16.548408087400325, 17.474486710146504), (13.762537310519251, 7.317228396657957), (0.5073387965977644, 16.44654789280768), (21.090919692334374, 0.4664956749952376), (4.978348911029578, 16.183283113879778), (4.654889985502283, 1.2726715815310041), (12.367154841190251, 13.665587400135662), (16.008399420782176, 18.537000235740884), (20.48335474733611, 20.67269487756411), (7.256540771852657, 4.38893617700217), (12.767253119789837, 20.602334580094187), (13.461895937603657, 15.042021079920657), (17.231140580573474, 0.5632466874270908), (8.245659647003151, 7.07643737394123), (2.8876816122438393, 22.156149638418164), (11.56083682590243, 5.89076845118566), (6.373560870037517, 6.789828398663972), (16.963768363338552, 5.9375063673907995), (4.7403148607683185, 12.525229722720226), (20.348526869687568, 8.360021287592268), (3.5786720063312987, 6.784085493530034), (7.689160458663727, 13.88186908053593), (7.422315779010543, 23.303448873006054), (8.30253532722054, 14.461903051378332), (10.734902468041527, 8.97109269874867), (2.6389358473871054, 8.192595878341507), (16.01974224079374, 11.068140485841482), (0.5535072634066718, 17.207707510371204), (18.372545979514353, 19.5915473959616), (10.655258622626931, 7.544046752655101), (21.22573217329034, 14.08146508137066), (21.961912452311992, 16.601368370990834), (8.685895982483094, 4.252567839127098), (15.368489681318682, 16.51403617778793), (1.6367775231518915, 10.32242648752582), (3.3937917601604917, 4.95062478238622), (20.14407768912631, 10.534894839242593), (15.391089438652433, 21.71675107059385), (24.11700835357872, 0.6823003023898572), (5.852006236232748, 15.836699085137496), (13.169904324742179, 3.560434543265684), (4.691765373220627, 12.690498126279227), (11.521219602261151, 1.0153244650503908), (10.868830183405887, 4.718572907384963), (16.942466068301936, 12.055383201821002), (19.995656450067518, 11.75953824126168), (0.5795443085679364, 2.9902462770437896), (18.486068510235494, 3.35334544744067), (22.36936113390868, 12.557119005152526), (18.861291250644786, 17.40894448179376), (21.58629382525529, 12.381276435192728), (2.4377678988635187, 18.315376952553347), (6.909505723649145, 17.463656321110204), (11.605607614024349, 20.634577431467175), (4.563410597029027, 7.8376962197779205), (21.568299386867054, 18.175019623067413), (1.0947982179697973, 14.37551994576797), (4.677536953407335, 8.319322592882417), (20.23809387255324, 13.341677284931725), (10.037925838354871, 11.664780510280462), (21.263619796466255, 13.047991158396123), (3.316150662277692, 13.46480738345365), (12.734785393871242, 2.4590211804913524), (11.844082675779417, 16.347753738121398), (18.80571213356935, 9.874444646810343), (23.21182002138006, 20.659244011328177), (9.526484717453904, 8.021553604669748), (17.625768771757237, 4.7511552518125635), (0.32754231689194613, 18.43256427153461), (18.821867974527425, 14.171961706801511), (0.5714413585934025, 23.248815437168187), (24.96087712358788, 0.13640906108525197), (24.63262277815805, 20.596715958204662), (1.0264238590903974, 8.358129870422971), (2.6952081299485924, 2.76685051175149), (19.826530812404666, 14.940664396515633), (20.80060840657415, 21.07639799743702), (11.262285879413126, 6.056721580791316), (10.997277708511898, 0.8209407269746366), (4.604526183597754, 0.8529408216766066), (12.307919610119807, 10.539489403169377), (15.605145352156669, 2.6383344584224004)]

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
                return updated_num
    print("Terminated.")
    return updated_num
                    

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
            



 

