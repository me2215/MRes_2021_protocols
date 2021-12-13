#------------------------------- PARAMTERS -------------------------------------
#--------------------------- Edit for each run ---------------------------------

# Amount of dry DNA indicated in the label of each oligo tube (nmol)
oligos_nmol = (28.4, 31.3, 25.1, 24.3, 33.2, 40.2, 50.1, 18.0, 43.6, 22.2, 24.6, 19.5, 32.7)

# Desired concentration of resuspended oligos (uM)
oligos_resusp_concentration = 100

# Desired concentrations in the salt gradient (mM)
test_gradient = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22]

# Number of replicates per gradient step
replicates = 8

# Concentration of salt Stock (mM)
salt_conc = 40

# Total volume in each well of the final assembled plate (ul)
total_rxn_vol = 40

# Will a scaffold strand be used?
scaffold = True

# Concentration of scaffold strand in the stock (nM)
scaffold_conc = 100


#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------


from opentrons import protocol_api
import math
import sys



# CALCULATIONS

# Number of oligo tubes to be resuspended
n_oligos = len(oligos_nmol)

# Volume that the oligos need to be resuspended in to reach the desired concentration
volume_added_to_oligos = [round(x / oligos_resusp_concentration * 1000) for x in oligos_nmol]

# Volume of oligo mix that needs to be added to each well in the final plate
mix_vol_single = total_rxn_vol/4

# Total volume of oligo mix that needs to be prepared to cover all wells
mix_volume = mix_vol_single * len(test_gradient) * replicates
mix_volume_rounded = math.ceil(mix_volume/100)*100

# Volume of scaffold that needs to be added to final mix (uL)
scaffold_in_mix = mix_volume_rounded/(scaffold_conc/(40))

# Calculate volumes of salt and buffer to create the gradient
salt_in = []
buffer_in = []

for i in test_gradient:
    mg = ((i * total_rxn_vol) / salt_conc)
    salt_in.append(mg)

    # Add buffer to make up to total rxn volume (+ oligo mix)
    buff = (total_rxn_vol - mg - mix_vol_single)
    buffer_in.append(buff)


# PARAMETER CHECK

# Check that the concentration of the salt stock is high enough
if salt_conc < max(test_gradient):
    protocol.pause('The concentration of the salt stock provided is too low to cover the gradient.')
    #print('The concentration of the salt stock provided is too low to cover the gradient.')
    #sys.exit()

# Check if number of replicates and gradient size is within the limits
if replicates > 8:
    protocol.pause('Too many repliactes! We cannot fit more than 8 replicates in a plate.')
    #print('Too many repliactes! We cannot fit more than 8 replicates in a plate.')
    #sys.exit()

if len(test_gradient) > 12:
    protocol.pause('Too many salt conditions! We cannot fit a salt gradient with more than 12 steps in a single plate.')
    #print('Too many salt conditions! We cannot fit a salt gradient with more than 12 steps in a single plate.')
    #sys.exit()

# Check oligo mix volumes
if mix_volume_rounded > 1400:
    protocol.pause('Total mix volme is too high to be handled.')
    #print('Total mix volme is too high to be handled.')
    #sys.exit()


if mix_volume_rounded < 200:
    protocol.pause('Mix volume is too small to be handled.')
    #print('Mix volume is too small to be handled.')
    #sys.exit()


#--------------------- PROTOCOL --------------------

metadata = {
    'protocolName': 'DNA Nanostructures and Buffer Dilutions',
    'author': 'MegaTron',
    'description': 'Test',
    'apiLevel': '2.11'
}

def run(protocol: protocol_api.ProtocolContext):

    # Define labware
    tiprack_1 = protocol.load_labware('opentrons_96_tiprack_300ul', 7)
    tiprack_2 = protocol.load_labware('opentrons_96_tiprack_20ul', 1)
    tiprack_3 = protocol.load_labware('opentrons_96_tiprack_20ul', 4)

    reservoir = protocol.load_labware('4ti0131_12_reservoir_21000ul', 5)

    # Tuberack 0 – original oligos
    tuberack = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', 3) #opentrons_24_tuberack_generic_2ml_screwcap

    # Tuberacks 2 and 3 – dilutions
    tuberack2 = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', 6) #opentrons_24_tuberack_generic_2ml_screwcap
    tuberack3 = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', 9) #opentrons_24_tuberack_generic_2ml_screwcap

    tempdeck = protocol.load_module('tempdeck', 10)
    tempplate = tempdeck.load_labware('opentrons_96_aluminumblock_biorad_wellplate_200ul', label='Temperature-Controlled Tubes')

    # Pipettes
    p300 = protocol.load_instrument('p300_single_gen2',  'left', tip_racks=[tiprack_1])
    p20 = protocol.load_instrument('p20_single_gen2', 'right', tip_racks = [tiprack_2, tiprack_3])


    #Step 1 - Resuspend oligos in standard buffer
    # to a uniform concentration to 100 uM

    p300.transfer(volume_added_to_oligos,
                  reservoir.columns()[0],
                  tuberack.wells()[0:n_oligos],
                  mix_after=(10, 100),
                  touch_tip=True,
                  blow_out= True,
                  blowout_location= 'destination well',
                  new_tip= 'always')

    # Let the oligos dissolve while preparing the gradient in the plate


    # Step 2 - Prepare 96-well plate with single gradient

    # Step 2.1 - Buffer

    # It only picks up the tips necessary to cover the volumes it's going
    # to pipette
    if min(buffer_in) > 20:
        p300.pick_up_tip()
    elif max(buffer_in) <= 20:
        p20.pick_up_tip()
    else:
        p300.pick_up_tip()
        p20.pick_up_tip()

    # Transferring Tris accross 96-well plate
    for n, x in enumerate(buffer_in):
        if x > 20:
            p300.distribute(x, reservoir.columns()[0],
                            tempplate.columns()[n][0:replicates],
                            touch_tip=False, blow_out=True,
                            new_tip='never')

        elif x <= 20:
            p20.distribute(x, reservoir.columns()[0],
                           tempplate.columns()[n][0:replicates],
                           touch_tip=False, blow_out=True,
                           new_tip='never')
        elif x < 2:
            protocol.comment('You are trying to pipette too small a volume! Please note results from this may not be accurate')
            p20.distribute(x, reservoir.columns()[0],
                           tempplate.columns()[n][0:replicates],
                           touch_tip=False, blow_out=True,
                           new_tip='never')
    # Drop tip
    if min(buffer_in) > 20:
        p300.drop_tip()
    elif max(buffer_in) <= 20:
        p20.drop_tip()
    else:
        p300.drop_tip()
        p20.drop_tip()


    # Step 2.2 - Salt stock

    # It only picks up the tips necessary to cover the volumes it's going
    # to pipette
    if min(salt_in) > 20:
        p300.pick_up_tip()
    elif max(salt_in) <= 20:
        p20.pick_up_tip()
    else:
        p300.pick_up_tip()
        p20.pick_up_tip()

    # Transferring salt buffer across the plate
    for n, x in enumerate(salt_in):
        if x > 20:
            p300.distribute(x, reservoir.columns()[1],
                            tempplate.columns()[n][0:replicates],
                            touch_tip=False, blow_out=True,
                            new_tip='never')

        elif x <= 20:
            p20.distribute(x, reservoir.columns()[1],
                           tempplate.columns()[n][0:replicates],
                           touch_tip=False, blow_out=True,
                           new_tip='never')
        elif x < 2:
            protocol.comment('You are trying to pipette too small a volume! Please note results from this may not be accurate')
            p20.distribute(x, reservoir.columns()[1],
                           tempplate.columns()[n][0:replicates],
                           touch_tip=False, blow_out=True,
                           new_tip='never')
    # Drop tip
    if min(salt_in) > 20:
        p300.drop_tip()
    elif max(salt_in) <= 20:
        p20.drop_tip()
    else:
        p300.drop_tip()
        p20.drop_tip()



    # Step 3 - Mix oligos and dilute

    # Maximum number of oligos per tube
    no_mixtogether = 10
    pipette_step = mix_volume_rounded/no_mixtogether # 1/10 of tube volume

    # Two types of tubes are going to be prepared:
    # - Type I tubes. A certain number of tubes with 10 different oligos each.
    # - Type II tube. A single tube with less than 10 oligos (the spare oligos)
    #                 that couldn't be accomodated in Type I tubes. Buffer will
    #                 be added to these tubes to adjust final volume.
    # (If the number of oligos to combine is < 10, no Type I tubes will be
    # prepared; only one Type II tube.)


    # First dilution (1:10 -> each oligo 10 uM)

    # How many Type I tubes are needed
    mixes = n_oligos//no_mixtogether 

    # Total number of tubes needed (Type I + Type II)
    total_mixes = mixes + 1

    # Number of spare oligos in the Type II tube
    final_mix = n_oligos%no_mixtogether

    # Prepare Type I tube(s) - if any
    for i in range(mixes):
        p300.transfer(pipette_step,
                      tuberack.wells()[i*10:(i*10+10)],
                      tuberack2.wells()[i],
                      touch_tip=False,
                      blow_out=True,
                      blowout_location='destination well',
                      new_tip='always')
        # Mix Type I tube only once, after having added all oligos, to save time
        p300.pick_up_tip()
        p300.mix(4, mix_volume_rounded/4, tuberack2.wells()[i])
        p300.drop_tip()

    # Prepare Type II tube
    p300.transfer(pipette_step,
                  tuberack.wells()[mixes*10:(mixes*10+final_mix)],
                  tuberack2.wells()[mixes],
                  touch_tip=False,
                  blow_out=True,
                  blowout_location='destination well',
                  new_tip='always')

    # Add buffer to Type II tube to adjust volume
    p300.transfer((mix_volume_rounded-pipette_step*final_mix),
                  reservoir.columns()[0], tuberack2.wells()[mixes],
                  touch_tip=False,
                  blow_out=True,
                  blowout_location='destination well',
                  new_tip='once')

    # Mix Type II tube only once, after all oligos and buffer have been added
    p300.pick_up_tip()
    p300.mix(4, mix_volume_rounded/4, tuberack2.wells()[mixes])
    p300.drop_tip()



    # Second dilution (1:10 -> each oligo 1 uM)

    # How many Type I tubes are needed
    mixes_second = total_mixes//no_mixtogether

    # Total number of tubes needed (Type I + Type II)
    total_mixes_second = mixes_second + 1

    # Number of spare oligos in the Type II tube
    final_mix_second = total_mixes%no_mixtogether

    # Prepare Type I tube(s) - if any
    for i in range(mixes_second):
        p300.transfer(pipette_step, tuberack2.wells()[i*10:(i*10+10)],
                      tuberack3.wells()[i],
                      touch_tip=False,
                      blow_out=True,
                      blowout_location='destination well',
                      new_tip='always')

        p300.pick_up_tip()
        p300.mix(4, mix_volume_rounded/4, tuberack3.wells()[i])
        p300.drop_tip()

    # Prepare Type II tube
    p300.transfer(pipette_step,
                  tuberack2.wells()[mixes_second*10:(mixes_second*10+final_mix_second)],
                  tuberack3.wells()[mixes_second],
                  touch_tip=False,
                  blow_out=True,
                  blowout_location='destination well',
                  new_tip='always')

    # Add buffer to Type II tube to adjust volume
    p300.transfer((mix_volume_rounded-pipette_step*final_mix_second),
                  reservoir.columns()[0], tuberack3.wells()[mixes_second],
                  touch_tip=False,
                  blow_out=True,
                  blowout_location='destination well',
                  new_tip='once')

    # Mix Type II tube only once, after all oligos and buffer have been added
    p300.pick_up_tip()
    p300.mix(4, mix_volume_rounded/4, tuberack3.wells()[mixes_second])
    p300.drop_tip()


    # Third dilution - (1:5 -> 200 nM each oligo)
    # Final mix (all oligos in a single tube). Maximum 1000 oligos, or 300 if
    # there is also a scaffold.

    # Number of spare oligos in the Type II tube
    final_mix_third = total_mixes_second%no_mixtogether
    # Pipette volume (1/5 of total tube volume)
    pipette_step3 = mix_volume_rounded/5

    # Transfer oligo mixture from previous step to last tube in tuberack 3
    p300.transfer(pipette_step3, tuberack3.wells()[0], tuberack3.wells()[-1],
              touch_tip=False,
              blow_out=True,
              blowout_location='destination well',
              new_tip='always')

    # Add scaffold (if there is any)
    if scaffold == True:
        p300.transfer((scaffold_in_mix),
                      tuberack3.wells()[3], tuberack3.wells()[-1],
                      touch_tip=False,
                      blow_out=True,
                      blowout_location='destination well',
                      new_tip='always')

        # Add buffer
        p300.transfer((mix_volume_rounded-pipette_step3*final_mix_third-scaffold_in_mix),
                      reservoir.columns()[0], tuberack3.wells()[-1],
                      touch_tip=False,
                      blow_out=True,
                      blowout_location='destination well',
                      new_tip='always')

    # If there is no scaffold, add buffer
    else:
        p300.transfer((mix_volume_rounded-pipette_step3*final_mix_third),
                      reservoir.columns()[0], tuberack3.wells()[-1],
                      touch_tip=False,
                      blow_out=True,
                      blowout_location='destination well',
                      new_tip='always')

    # Mix final oligo mix
    p300.pick_up_tip()
    p300.mix(4, mix_volume_rounded/4, tuberack3.wells()[-1])
    p300.drop_tip()

    # Add DNA to heatdeck PCR tray.
    # Concentration 50 nM for oligos and 10 nM for scaffold.
    for row in range(replicates):
        for col in range(len(test_gradient)):
            p20.transfer(total_rxn_vol/4,
                         tuberack3.wells()[-1],
                         tempplate.columns()[col][row],
                         mix_after=(3, total_rxn_vol/4),
                         touch_tip=False, blow_out=True,
                         blowout_location='destination well',
                         new_tip='always')



    #Step 4 - Heating and Cooling Plate
      #Heat quickly and cool slowly according to Sigma-Aldrich 'Annealing Oligos Protocol'

    #Heating step
    tempdeck.set_temperature(90)
    protocol.comment('Incubating at 90˚C')
    protocol.delay(minutes = 5)

    #Cooling
    tempdeck.set_temperature(70)
    protocol.comment('Beginning cooldown')
    protocol.delay(minutes = 15)

    tempdeck.set_temperature(50)
    protocol.delay(minutes = 15)

    tempdeck.set_temperature(30)
    protocol.delay(minutes = 15)

    tempdeck.set_temperature(4)
    protocol.comment('Cooling to 4˚C for storage')
    protocol.delay(minutes = 5)
