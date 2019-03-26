# WSN Simulation
A simulation code of wireless sensor network. The code simulates the situation that sink node disseminate code to the network. The simulation ends when all the sensor nodes in the network has received the code.
## run simulation
> run_sim(simulation_times,ABRCD=True/False,adapt_duty_cycle=True/False)

## display network deployment
> display_net(network)

output:
Sink node is represented by a red triangle, and the other sensor nodes are represented by green vertexes.
<img src="./img/net_500.png"></img>
## display energy residual hexagonal binning plot
> display_energy_residual_heatmap(network, the_remaining_energy_of_network)

output:
The darker hexagon imply higher battery level
<img src="./img/adaptive_radius.png"></img>
