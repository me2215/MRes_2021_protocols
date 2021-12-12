import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import pandas as pd
import itertools
from itertools import cycle
from tkinter.ttk import Entry, Button, Label

#Application class contains all functions needed to run GUI and dialogs.
class Application:
    def __init__(self, master):
        # set up frame
        self.master = master
        self.frame = tk.Frame(self.master)
        master.title("Parts combinations")
        master.minsize(400, 200)
        #Path strings.
        self.input_parts_path = tk.StringVar()
        self.platemap_save_path = tk.StringVar()
        self.template_path = tk.StringVar()
        self.final_script_save_path = tk.StringVar()



        #Intro information - the paths need to be set before the final "Generate..." button is pressed.
        self.label_intro = Label(master,
                                 text="Welcome to the Isaac_Newtron app! This application allows you to input \n a .csv file containing parts to be assembled into novel constructs")

        self.label_input_parts = Label(master,
                                       text="Select .csv file containing parts to be assembled in final construct")

        self.input = Label(master, text="Input:")
        self.input_entry = Entry(master, textvariable=self.input_parts_path)
        self.input_path_button = Button(master, text="Browse...", command=self.browse_input_file)

        #Set platemap combinations file.
        self.label_platemap_save = Label(master,
                                         text="Select save location of final assembled plate map file")
        self.output_platemap = Label(master, text="Output:")
        self.output_entry = Entry(master, textvariable=self.platemap_save_path)
        self.output_path_button = Button(master, text="Browse...", command=self.browse_platemap_file)
        self.label_template_select = Label(master,
                                           text="Select template .py file to generate OT-2 protocol from")

        #Template file.
        self.template = Label(master, text="Template:")
        self.template_entry = Entry(master, textvariable=self.template_path)
        self.template_path_button = Button(master, text="Browse...", command=self.browse_template_file)

        #Protocol.
        self.label_protocol_save = Label(master,
                                         text="Select save location of final OT-2 protocol file")
        self.final_script = Label(master, text="Protocol:")
        self.final_script_entry = Entry(master, textvariable=self.final_script_save_path)
        self.final_script_path_button = Button(master, text="Browse...", command=self.browse_final_script_file)
        self.generate_platemap_button = Button(master, text="Generate plate map and OT-2 protocol", command=self.run_combinations)

        #Layout.
        self.label_intro.grid(row=0, column=0, pady=(0, 10), columnspan=3)
        self.label_input_parts.grid(row=1, column=0, columnspan=3)

        self.input.grid(row=2, column=0)
        self.input_entry.grid(row=2, column=1, sticky="EW")
        self.input_path_button.grid(row=2, column=2)

        self.label_platemap_save.grid(row=3, column=0, pady=(10, 0), columnspan=3)
        self.output_platemap.grid(row=4, column=0)
        self.output_entry.grid(row=4, column=1, sticky="EW")
        self.output_path_button.grid(row=4, column=2)

        self.label_template_select.grid(row=5, column=0, pady=(10, 0), columnspan=3)
        self.template.grid(row=6, column=0)
        self.template_entry.grid(row=6, column=1, sticky="EW")
        self.template_path_button.grid(row=6, column=2)


        self.label_protocol_save.grid(row=7, column=0, pady=(10, 0), columnspan=3)
        self.final_script.grid(row=8, column=0)
        self.final_script_entry.grid(row=8, column=1, sticky="EW")
        self.final_script_path_button.grid(row=8, column=2)

        self.generate_platemap_button.grid(row=9, column=1, pady=(10,10))




    def file_save(self, write_data, f): #Argument passed = data to be written to .csv file.
            write_data.to_csv(f, index=False)


    def run_combinations(self):
        filename = self.input_parts_path.get()  #Open dialog box to search for path of input .csv file.
        #Store in df = combs (short for combinations).
        combs = pd.read_csv(filename)
        plate = Plate(combs)  #Run functions in class Plate using contents of input .csv file as argument.
        prom_utr_tuple = plate.prom_utr_lengths() #prom_utr_lengths = function to define lengths of .csv promoter and UTR columns.
        platemap_df = plate.platemap(prom_utr_tuple[0], prom_utr_tuple[1]) #The tuple contains: (number of promoters, number of UTRs).
        #Used to define dataframe containing all combinations of parts in platemap to be outputted to new .csv file.

        tk.messagebox.showinfo("Plate map complete",
                               "Plate map completed. Saving to specified path.") #Tells the user that it's done.
        self.file_save(platemap_df, self.platemap_save_path.get()) #Saves the file in the location specified.

        plate.write_protocol(self.final_script_save_path.get(), self.template_path.get(), prom_utr=prom_utr_tuple)
        tk.messagebox.showinfo("Protocol complete",
                               "OT-2 protocol completed. Saving to specified path.")

    def browse_input_file(self):
        filename = filedialog.askopenfilename(initialdir="/", title="Select a File",
                                              filetypes=(("CSV Files", "*.csv"), ("All Files", "*.*"))) #Open dialog box.
        self.input_parts_path.set(filename)

    def browse_platemap_file(self):
        filename = filedialog.asksaveasfilename(defaultextension=".csv", initialdir="/", title="Save File",
                                      filetypes=(("CSV Files", "*.csv"), ("All Files", "*.*")))
        self.platemap_save_path.set(filename)

    def browse_template_file(self):
        filename = filedialog.askopenfilename(initialdir="/", title="Select a File",
                                              filetypes=(("Python Files", "*.py"), ("All Files", "*.*"))) #Open dialog box.
        self.template_path.set(filename)

    def browse_final_script_file(self):
        filename = filedialog.asksaveasfilename(defaultextension=".py", initialdir="/", title="Save File",
                                                filetypes=(("Python Files", "*.py"), ("All Files", "*.*"))) #Open dialog box.
        self.final_script_save_path.set(filename)


#Plate class contains all functions needed to calculate desired output depending on user inputs from Application class GUI.
class Plate:
    def __init__(self, combs):
        self.rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        self.columns = list(range(1, 13))  # 1 ... 12
        # determines 96-well plate coordinates
        self.promoters = combs['Promoters'].dropna().tolist()
        self.utr = combs['3UTRs'].dropna().tolist()
        #If the number of promoters =/= number of utr, then Python reads as NaN cells. These are deleted and the columns of the dataframe are converted into lists for easy manipulation.

    def prom_utr_lengths(self): #To get the number of promoters and utrs, stored in tuple.
        n_promoters = len(self.promoters)
        n_utr = len(self.utr)
        return n_promoters, n_utr



    def write_protocol(self, ot2_script_path, template_path, **kwargs):
        """Generates an ot2 script where kwargs are
        written as global variables at the top of the script. The remainder of template file is subsequently written below.
        """
        with open(ot2_script_path, 'w') as wf: #Open file to write to.
            with open(template_path, 'r') as rf: #Open .py containing template code (all of M5 except global var).
                for index, line in enumerate(rf):
                    if line[:3] == 'def':  #Finds function start.
                        function_start = index
                        break
                    else:
                        wf.write(line)  #Writes contents of template .py to new protocol file.


                for key, value in kwargs.items():
                    wf.write(key + ' = ' + str(value))
                    wf.write('\n')
                wf.write('\n')
            with open(template_path, 'r') as rf:
                for index, line in enumerate(rf):
                    if index >= function_start - 1:
                        wf.write(line)


    def platemap(self, n_promoters, n_utr): #Function to output platemap of resulting construct combinations.
        platemap_df = pd.DataFrame()
        total = n_promoters * n_utr #Total number of combinations possible.

        #First need to identify which part of the 96-well plate is actually going to be filled if total < 96.
        map_coords = itertools.product(self.rows, self.columns) #Gets coordinates A1, A2 ... H12 as tuples by iterating through rows and columns lists.
        coords = [''.join(map(str, x)) for x in map_coords] #Converts tuples to strings. len(coord) = 96.
        coords.sort(key=lambda x: int(x[1:])) #Sort by column, same as Opentrons pipette; A1-H1, A2-H2 etc.
        platemap_df['Platemap Coordinates'] = coords[:total] #Slice to only include the number of cells containing promoter+UTR mix in final library.

        seq = cycle(self.promoters) #In our pattern of pipetting, each promoter is pipetted in a new cell vertically downwards.
        #So generate cycle of promoters to iterate through and populate df eg. 7 promoters, A1 -> A1, H1, G2 etc.
        platemap_df['Promoters'] = [x for x, _ in zip(seq, platemap_df['Platemap Coordinates'])] # iteration
        platemap_df["3'UTRs"] = list(
            itertools.chain.from_iterable(itertools.repeat(x, len(self.promoters)) for x in self.utr)) #Repeats every element in list of UTRs vertically downwards eg. 3 UTRs, A1 -> A1, B1, C1, D1, E1, F1, G1 ; B2 -> H1, A2 etc.
        return platemap_df


def main():
    root = tk.Tk()
    app = Application(root)
    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=3)
    root.columnconfigure(2, weight=1)
    root.mainloop()


if __name__ == '__main__':
    main()

