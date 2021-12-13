# Automated Combinatorial Golden Gate and Transformation - Isaac Newtron

## Introduction
The Isaac Newtron team (Jacopo Gabrielli, Leo Gornovskiy, Luis Enrique García Riveira, Menglu Wu, Shi Yi and Sifeng Chen) is presenting a protocol for the automation of combinatorial Golden Gate cloning. In practice, our app can be used to automate cloning protocols where there is a fixed vector backbone (part 1) and a fixed DNA part (part 3) and two variable DNA parts (part 2 and 4) for which multiple variants have to be tested in combination. For example, part 1 could be a generic plasmid backbone, part 3 a 5'UTR + coding sequence, and parts 2 and 4 could be respectively the promoter and the 3'UTR. As the promoter influences the transcription rate, therefore, the amount of mRNA produced, and the 3'UTR, the mRNA stability, testing multiple combinations allows to optimise the construct for desired properties of the mRNAs. For example, we might want a low quantity of mRNA and high stability or the opposite. Moreover, this protocol could illuminate the combinatorial behaviour of the two parts, such as possible undesired interactions and folding of the DNA structure due to homologies in the sequences. 

## Contents
The submission comprises 3 files: 
- GUI_Isaac_Newtron.py
- Template_Protocol_Isaac_Newtron.py
- Combinations_Isaac_Newtron.csv

GUI_Isaac_Newtron.py - The Graphical User Interface through which the users' designs are uploaded in a ".csv" format. The ".py" file can be compiled in any Python compiler or IDE. The app also creates and saves a protocol for the combinatorial assembly of the two parts in ".py" format which can be run in the OpenTron without further modifications. Furthermore, the app will create and save a file in ".csv" format informing the user on the final plate layout with the well name written as "Letter + Number" and the combination written as "part 2 part 4".

Template_Protocol_Isaac_Newtron.py - The template which GUI_Isaac_Newtron.py uses to write the customised protocol based on the information from the ".csv" file uploaded. The protocol starts from a number of parts 2 and 4 and performs Golden Gate assembly using an assembly mix, water, and parts 1 and 3 in a thermocycler. Following, it transfers part of the final assembly into a spare plate for storage purposes and it adds cells (which are held in a temperature block at 4°C until then) into the remaining construct to do a heat shock transformation in the thermocycler. 

Combinations_Isaac_Newtron.csv - An example of a ".csv" file containing a number of promoters and UTRs listed vertically under their respective headers. This can be modified to the user's needs and uploaded on GUI_Isaac_Newtron.py to generate a customised protocol.
