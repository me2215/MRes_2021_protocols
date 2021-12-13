#!/usr/bin/env python
# coding: utf-8

# In[3]:


# -*- coding: utf-8 -*-

from opentrons import simulate
metadata = {'apiLevel': '2.8'}
protocol = simulate.get_protocol_api('2.8')

#Example tuple for simulation purposes: this, in the robot version, would be generate by the GUI_Isaac_Newtron.py file. 

prom_utr = (3,5)
#def run(protocol:protocol_api.ProtocolContext):   #Commented out for simulation purposes. 
  #def IN_assembly_transformation(prom_utr):       #Commented out for simulation purposes. 

#Extract lengths from tuple: 
n_promoters = prom_utr[0]
n_utr = prom_utr[1]
#Load and set-up labware.
tiprack_20 = protocol.load_labware('opentrons_96_tiprack_20ul', 3)
tiprack_20_2 = protocol.load_labware('opentrons_96_tiprack_20ul', 2)
tiprack_20_3 = protocol.load_labware('opentrons_96_tiprack_20ul', 1)
reservoir_const = protocol.load_labware('nest_96_wellplate_2ml_deep', 6) # constant reservoir = all parts that are consistent between constructs = destination plasmid in assembly mix + ligase buffer (A1) and 5U-CDS (A2).
reservoir_var = protocol.load_labware('corning_96_wellplate_360ul_flat', 5) #Contains all promoters and 3'UTRs to be combined.
tc_mod = protocol.load_module('Thermocycler module') #Default position of thermocycler is slot 7, 8, 10, 11.
temperature_module = protocol.load_module('temperature module', 4)
cells_plate = temperature_module.load_labware('biorad_96_wellplate_200ul_pcr')
PCR_plate = tc_mod.load_labware('biorad_96_wellplate_200ul_pcr')
spare_plate = protocol.load_labware('biorad_96_wellplate_200ul_pcr', 9) #To hold the rest of the final assembly that we're not transforming. 
#Pipettes.
p20s = protocol.load_instrument('p20_single_gen2', 'right', tip_racks=[tiprack_20, tiprack_20_2, tiprack_20_3])
p20 = protocol.load_instrument('p20_multi_gen2', 'left', tip_racks=[tiprack_20, tiprack_20_2, tiprack_20_3])
#Set up heat block for cells on ice in case it was not already set manually from the OpenTron software. 
temperature_module.set_temperature(4)


#Set up assembly mix with destination plasmid straight into thermocycler module.
if tc_mod.lid_position != 'open':
  tc_mod.open_lid() #Open the lid of the thermocycler in case it was closed. 
rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G','H'] #Define plate rows.
columns = list(range(1, 13)) #Define plate columns.
p20.pick_up_tip()
#Work out the minimum number of columns to pipette when using the multichannel to optimise tips usage. 
if n_promoters*n_utr%8 == 0: 
  min_num_cols = n_promoters*n_utr/8
else: 
  min_num_cols = (n_promoters*n_utr//8)+1

for i in range(min_num_cols):
  p20.transfer(14, reservoir_const['A1'], PCR_plate[f'A{columns[i]}'], new_tip='never') #A1 in reservoir_const = assembly mix + plasmid
p20.drop_tip()
p20.pick_up_tip()
for i in range(min_num_cols):
  p20.transfer(2, reservoir_const['A2'], PCR_plate[f'A{columns[i]}'], new_tip='never') #A2 in reservoir_const = 5'UTR + CDS sequence.
p20.drop_tip()

#Code to transfer sample from an indexed source plate to the destination PCR plate with combination logic.

for i in range(n_promoters):
  for e in range(n_utr):
    dest_prom = n_promoters * e + i 
    p20s.transfer(2, reservoir_var[f'{rows[i % 8]}{columns[i // 8]}'], PCR_plate[f'{rows[dest_prom % 8]}{columns[dest_prom // 8]}'],mix_after = (3,5), new_tip='once') #If 3 promoters and 3 UTRs, here it goes from A1 of source to A1, D1, G1 of destination. Then from A2 of source to B1, E1, H1 of destination. Then from A3 of source to C1, F1, A2 of destination. 

d = 0
for i in range(n_utr): 
  for e in range(n_promoters):
    dest_utr = i + n_promoters 
    p20s.transfer(2, reservoir_var[f'{rows[dest_utr % 8]}{columns[dest_utr // 8]}'], PCR_plate[f'{rows[d % 8]}{columns[d // 8]}'], mix_after= (3,5), new_tip = 'once') #If 3 promoters and 3 UTRs, here it goes from A4 of source to A1, B1, C1 of destination. Then from A5 of source to D1, E1, F1 of destination. Then from A6 of source to G1, H1, A2 of destination. 
    d+=1
#Incubation protocol.
if tc_mod.lid_position != 'closed':
  tc_mod.close_lid()

#Set the lid temperature before executing a thermocycler profile (37-110 °C).
#Define a thermocycler profile: 37°C, 1 hr → 60°C, 5 min.
profile = [{'temperature': 37, 'hold_time_minutes': 60},{'temperature': 60, 'hold_time_minutes': 5}]
#Execute the profile.
tc_mod.execute_profile(steps=profile, repetitions=1,
                          block_max_volume=20)

# define heat-shock profile: 4°C, 30min ; 42°C, 30 sec
heat_shock_profile = [{'temperature': 4, 'hold_time_minutes': 30},{'temperature': 42, 'hold_time_minutes': 0.5}]

if tc_mod.lid_position != 'open':
  tc_mod.open_lid() #Open the lid of the thermocycler. 

tc_mod.set_block_temperature(4) # 'on ice'
#Set a pause to reload the tip racks as the following steps require a substantial number of tips, depending on the number of combinations. 
protocol.pause("Switch out empty tip racks")
p20.reset_tipracks()
p20s.reset_tipracks()
#Set up transformation with 3uL DNA, 20uL cells. 
for i in range(min_num_cols):
  p20.transfer(17, PCR_plate[f'A{columns[i]}'], spare_plate[f'A{columns[i]}']) #Leave only 3uL in the thermocycler using multichannel pipette and store the rest in a different plate. 
  p20.transfer(20, cells_plate[f'A{columns[i]}'], PCR_plate[f'A{columns[i]}']) #Add 20uL of cells to thermocycler.
if tc_mod.lid_position != 'closed':
  tc_mod.close_lid()

#Execute the heat-shock profile.
tc_mod.execute_profile(steps=heat_shock_profile, repetitions=1,
                          block_max_volume=21)
if tc_mod.lid_position != 'open':
  tc_mod.open_lid() #Open the lid of the thermocycler.


#IN_assembly_transformation(prom_utr = prom_utr) #Define the global variable using the tuple generated by our app (GUI_Isaac_Newtron.py). Commented out as it would not work in the simulation given that prom_utr is not generated by the GUI here. 

for line in protocol.commands():
    print(line)


# In[ ]:




