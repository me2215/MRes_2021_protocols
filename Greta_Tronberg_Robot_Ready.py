#!/usr/bin/env python
# coding: utf-8

# In[ ]:


## Golden Gate Assembly for a promoter and CDS library for Yarrowia Toolkit 

from opentrons import protocol_api

metadata = {
    'protocolName':'Protocol',
    'author':'Team2 <yolo@gmail.com>',
    'description':'Ally,Tom,Cathal,Will,Alex - Opentrons adventure',
    'apiLevel': '2.8'}

def run(protocol: protocol_api.ProtocolContext):

    #Labware (keep aluminium block tuberack in freezer until setup)
    tiprack1 = protocol.load_labware('opentrons_96_tiprack_20ul', 2) 
    tiprack2 = protocol.load_labware('opentrons_96_tiprack_300ul', 3)
    tiprack3 = protocol.load_labware('opentrons_96_tiprack_20ul', 5)
    tiprack4 = protocol.load_labware('opentrons_96_tiprack_300ul', 6)

    heatblock = protocol.load_module('tempdeck', 4)
    plate1 = heatblock.load_labware('4ti_96_wellplate_200ul')

    thermocycler = protocol.load_module('Thermocycler Module')
    plate2 = thermocycler.load_labware('4ti_96_wellplate_200ul')

    tuberack = protocol.load_labware('opentrons_24_aluminumblock_nest_1.5ml_snapcap', 1)

    #pipette
    p20 = protocol.load_instrument('p20_single_gen2', 'right', tip_racks=[tiprack1, tiprack3])
    p300 = protocol.load_instrument('p300_single_gen2', 'left', tip_racks=[tiprack2, tiprack4])

    promoters = 3
    genes = 3

    ##commands

    #set block to 4 degrees
    heatblock.set_temperature(4)

    # set the initial temperature of the thermocycler to 4
    thermocycler.set_block_temperature(4)

    ##pipette into plate in thermocycler

    columns = [['A1', 'B1', 'C1', 'D1', 'E1', 'F1', 'G1', 'H1'], ['A2', 'B2', 'C2', 'D2', 'E2', 'F2', 'G2', 'H2'], ['A3', 'B3', 'C3', 'D3', 'E3', 'F3', 'G3', 'H3'], ['A4', 'B4', 'C4', 'D4', 'E4', 'F4', 'G4', 'H4'], ['A5', 'B5', 'C5', 'D5', 'E5', 'F5', 'G5', 'H5'], ['A6', 'B6', 'C6', 'D6', 'E6', 'F6', 'G6', 'H6'], ['A7', 'B7', 'C7', 'D7', 'E7', 'F7', 'G7', 'H7'], ['A8', 'B8', 'C8', 'D8', 'E8', 'F8', 'G8', 'H8'], ['A9', 'B9', 'C9', 'D9', 'E9', 'F9', 'G9', 'H9'], ['A10', 'B10', 'C10', 'D10', 'E10', 'F10', 'G10', 'H10'], ['A11', 'B11', 'C11', 'D11', 'E11', 'F11', 'G11', 'H11'], ['A12', 'B12', 'C12', 'D12', 'E12', 'F12', 'G12', 'H12']]

    rows = [['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9', 'A10', 'A11', 'A12'], ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9', 'B10', 'B11', 'B12'], ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'C10', 'C11', 'C12'], ['D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'D9', 'D10', 'D11', 'D12'], ['E1', 'E2', 'E3', 'E4', 'E5', 'E6', 'E7', 'E8', 'E9', 'E10', 'E11', 'E12'], ['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12'], ['G1', 'G2', 'G3', 'G4', 'G5', 'G6', 'G7', 'G8', 'G9', 'G10', 'G11', 'G12'], ['H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'H7', 'H8', 'H9', 'H10', 'H11', 'H12']]

    #define all destination wells
    TC_all = []
    for i in range(genes):
        TC_all += columns[i][:promoters]

    #define CDS and vector destination wells
    TC_columns = []
    for i in range(genes):
        TC_columns.append(columns[i][:promoters])

    #define promoter destination wells
    TC_rows = []
    for i in range(promoters):
        TC_rows.append(rows[i][:genes])

    #pipette MasterMix into all wells
    p300.distribute(
        14,
        tuberack['A1'],
        [plate2.wells_by_name()[well_name] for well_name in TC_all],
        air_gap = 0)

    #pipette promoters 
    for i in columns[0][:promoters]:
        for j in TC_rows[columns[0].index(i)][:]:
            p20.transfer(
                2,
                plate1.wells(i),
                plate2.wells(j),
                air_gap = 2,
                blow_out = True)

    #pipette CDS
    for i in columns[1][:genes]:
        for j in TC_columns[columns[1].index(i)][:]:
                p20.transfer(
                2,
                plate1.wells(i),
                plate2.wells(j),
                air_gap = 2,
                blow_out = True)

    #pipette vectors - vectors go into the same wells as CDS
    for i in columns[2][:genes]:
        for j in TC_columns[columns[2].index(i)][:]:
                p20.transfer(
                2,
                plate1.wells(i),
                plate2.wells(j),
                air_gap = 2,
                blow_out = True)

    #run the thermocycler for assembly
    thermocycler.close_lid()
    thermocycler.set_lid_temperature(100)

    profile = [
        {'temperature': 37, 'hold_time_seconds': 300},
	{'temperature': 16, 'hold_time_seconds': 300},]

    thermocycler.execute_profile(steps=profile, repetitions=35, block_max_volume=20)

    #heatshock for killing enzymes 
    profile = [{'temperature': 70, 'hold_time_minutes': 10}]

    thermocycler.execute_profile(steps=profile, repetitions=1, block_max_volume=20)

    thermocycler.set_block_temperature(4)

    thermocycler.open_lid()

    #while the thermocycler is running, put the aluminium block in the freezer to keep the competent cells cold

    #pipette 50 uL of competent cells into each construct
    for j in TC_all:
        p300.transfer(
        50,
        tuberack['A2'],
        plate2.wells(j),
        air_gap = 2,
        blow_out = True)

    #heat shock step
    thermocycler.close_lid()
    thermocycler.set_lid_temperature(37)

    profile = [
        {'temperature':42, 'hold_time_seconds':45},
        {'temperature':4, 'hold_time_minutes':1}]
    thermocycler.execute_profile(steps=profile, repetitions=1, block_max_volume=60)
    thermocycler.open_lid()

    #recovery - add SOC into each construct+cells 
    for j in TC_all:
        p300.transfer(
        50,
        tuberack['A3'],
        plate2.wells(j),
        air_gap = 2,
        blow_out = True)

    thermocycler.close_lid()
    thermocycler.set_lid_temperature(37)

    profile = [
        {'temperature': 37, 'hold_time_minutes': 60},]
    thermocycler.execute_profile(steps=profile, repetitions=1, block_max_volume=60)
    thermocycler.open_lid()

    #plate cells out of opentrons onto agar plate
    #put agar plate into incubator overnight

