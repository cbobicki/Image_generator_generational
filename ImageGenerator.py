import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import numpy as np
import colorspacious as cs
from timeit import default_timer as timer


#Caleb Bobicki T00618738 AI Final Project 
v = ""
class ImageGenerator:
    def __init__(self, master): #GUI layout setup 
        self.master = master
        self.master.title("Image Generator") 
        self.selected_image = None
        self.fitness_variation = tk.StringVar()
        self.image_label = tk.Label(self.master)
        self.image_label.pack(pady=20)
        self.select_button = tk.Button(self.master, text="Select Image", command=self.selectimage)
        self.select_button.pack(pady=5)
        self.accept_button = tk.Button(self.master, text="Save Image", command=self.saveimage)
        self.accept_button.pack(pady=5)
        self.fitness_label = tk.Label(self.master, text="Fitness Variation:")
        self.fitness_label.pack()
        self.fitness_entry = tk.Entry(self.master, textvariable=self.fitness_variation)
        self.fitness_entry.pack()
        self.generate_button = tk.Button(self.master, text="Generate", command=self.generateimage, state=tk.DISABLED)
        self.generate_button.pack(pady=10)
        global percentage
        self.percentage=tk.Label(self.master, text="")
        self.percentage.pack()
        global timetext
        self.timetext=tk.Label(self.master, text="")
        self.timetext.pack()
        self.master.geometry("500x500")

    def selectimage(self): #Using Tkinter opens a file prompt for a image
        file_path = filedialog.askopenfilename(title="Select Image File", filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
        if file_path: #when found open and put the image on the gui
            self.selected_image = Image.open(file_path)
            self.update_image()
           
    #Had some help with this for understanding the cs libary and what XYZ100_w/D65 means          
    def rgbtolab(self, rgb_values):
        lab_values = cs.cspace_convert(rgb_values, start={"name": "sRGB1"}, end={"name": "CIELab", "XYZ100_w": "D65"})  #using cspace converts the rgb value into a lab value
        return lab_values
    
    def labtorgb(self, lab_value):
        rgb_value = cs.cspace_convert(lab_value, start={"name": "CIELab", "XYZ100_w": "D65"}, end={"name": "sRGB1"}) #using cspace converts the lab value back into a rgb value
        rgb_value = np.clip(rgb_value, 0.0, 1.0) #standardizes the rgb values between 0.0 and 1.0 
        return rgb_value

    def getdistances(self, lab1, lab2): #Lab 2 will always be the fitness lab so we can return lab1 to get the original lab color
        delta_e = cs.deltaE(lab1, lab2, input_space={"name": "CIELab"}, uniform_space={"name": "CIELab"}) #using the deltaE gets the distance between two color lab values
        return delta_e,lab1
    
    
    def crossover(self, rgb1, rgb2):#picks a random spot in the rgb array and crosses them over
        rgb1 = np.array(rgb1)
        rgb2 = np.array(rgb2) 
        crossover_point = np.random.randint(1, len(rgb1))
        new_rgb1 = np.concatenate([rgb1[:crossover_point], rgb2[crossover_point:]])
        new_rgb2 = np.concatenate([rgb2[:crossover_point], rgb1[crossover_point:]])
        return new_rgb1, new_rgb2
    
    def mutate(self, rgb): #picks a random spot in the rgb array and mutates it at a rate of 50% 
        mutation_mask = np.random.rand(len(rgb)) < 0.5
        mutated_rgb = rgb + mutation_mask * np.random.normal(scale=0.1, size=len(rgb))
        mutated_rgb = np.clip(mutated_rgb, 0.0, 1.0)
        return mutated_rgb
                    
 
    def update_image(self): #updates the image on the gui 
        if self.selected_image:
            image = ImageTk.PhotoImage(self.selected_image)
            self.image_label.config(image=image)
            self.image_label.image = image 
            self.master.geometry(f"{self.selected_image.width + 500}x{self.selected_image.height + 500}")

    def saveimage(self): #accepts the image filepath and writes the values onto a fitness text file for reference
        if self.selected_image:
            pixel_values = np.array(self.selected_image)
            file_path = "fitness.txt"
            np.savetxt(file_path, pixel_values.reshape(-1, 3), fmt="%d", delimiter=",")
            self.generate_button["state"] = tk.NORMAL
            print("Fitness Variation: ",self.fitness_variation.get())
            print("Pixel values saved to: ", file_path)
        else:
            self.generate_button["state"] = tk.DISABLED #cant generate without a image
            print("Please select an image.")

    def generateimage(self):
        if self.fitness_variation.get():
            try:
                global timetext
                self.timetext["text"]= ("")
                self.timetext.pack()
                start = timer() #starts timer
                file_path = "fitness.txt" #gets filepath
                pixel_values = np.loadtxt(file_path, delimiter=",") #loads array from fitness text
                count = int(pixel_values.size/3) #gets the amount of items in array /3 (3 values in each item)
                #print(count)
                integer_array = pixel_values.astype(np.int32) #convert to a int array
                integer_array = integer_array / 255 #divides into ranges between 0.0 and 1.0
                finalarray = [] #creates the final array which gets projected out
                #dimensions = np.shape(integer_array) #Debug lines
                #total_items = np.size(integer_array)
                #print("Dimensions of the 3D array:", dimensions)
                #print("Total number of tuple items:", total_items)
         
                varation = float(self.fitness_variation.get())  #gets varation from user
                for i in range(count): #loops throught array
                    fv = integer_array[i] #gets first value from array                    
                    p1= np.round(np.random.rand(3), 2) #creates p1 and p2 from a random color
                    p2= np.round(np.random.rand(3), 2)
                    c1,c2 = self.crossover(p1, p2) #creates c1 and c2 from crossing over p1 and p2
                    c1 = self.mutate(c1) #mutates each rgb value
                    c2 = self.mutate(c2)
                    pl1 = self.rgbtolab(p1) #converts them all to a lab value
                    pl2 = self.rgbtolab(p1)
                    cl1 = self.rgbtolab(c1)
                    cl2 = self.rgbtolab(c2)
                    f1 = self.rgbtolab(fv)
                    delta_e = self.getdistances(pl1, f1),self.getdistances(pl2, f1),self.getdistances(cl1, f1),self.getdistances(cl2, f1) #calculates distance and returns the distance with the lab value 
                    sorted_delta_e = sorted(delta_e, key=lambda x: x[0]) #sorts the array so the closest distance is always first
                    sorted_arrays = [values[1] for values in sorted_delta_e]  #get the lab value from the array                
                    while True: #same as before but loop until the sorted distance first value is less or equal to the variation
                         p1 = self.labtorgb(sorted_arrays[0])
                         p2 = self.labtorgb(sorted_arrays[1])
                         c1,c2 = self.crossover(p1, p2)
                         c1 = self.mutate(c1)
                         c2 = self.mutate(c2)
                         pl1 = self.rgbtolab(p1)
                         pl2 = self.rgbtolab(p1)
                         cl1 = self.rgbtolab(c1)
                         cl2 = self.rgbtolab(c2)
                         f1 = self.rgbtolab(integer_array[i])
                         delta_e = self.getdistances(pl1, f1),self.getdistances(pl2, f1),self.getdistances(cl1, f1),self.getdistances(cl2, f1)
                         sorted_delta_e = sorted(delta_e, key=lambda x: x[0]) #still created a semi pic with varation because it takes the best value outta all of them
                         sorted_arrays = [values[1] for values in sorted_delta_e]
                         
                         #print("distance to variation: ", round(sorted_delta_e[0][0],2))
                         if round(sorted_delta_e[0][0],2) <= varation: 
                            rgbv = self.labtorgb(sorted_arrays[0]) #gets the lab value that meets the distance condition and converts it back to rgb
                            rgbv = rgbv * 255 #converts from 0.0-1.0 format to 255 
                            rgbv = rgbv.astype(int) #converts to int to clean it up
                            finalarray.append(rgbv) #adds to the final array
                            f = i / count #this is just use to tell me how long until the image is generated IE until array is filled
                            p = round(float(f * 100),2)       
                            print(p,"%")
                            global percentage
                            self.percentage["text"]= "Generating image:", p,"%"
                            self.percentage.pack()
                            
                            self.master.update()
                            break
                end = timer()
                time = (end-start) / 60
                print("Function took:", round(time,2) , "minutes") #checking how long to complete generation
                global timetext
                self.timetext["text"]= ("Image took:", round(time,2) , "minutes to generate")
                self.timetext.pack()
                        
                finalarray = np.array(finalarray) #converts to nparray
                finalarray = finalarray.reshape((self.selected_image.height, self.selected_image.width, 3)) #reshapes into original image space 
                generate_window = tk.Toplevel(self.master) #makes new window
                generate_window.title("Generated Image") #titles window
                generated_image = Image.fromarray(np.uint8(finalarray)) #creates image object from array 
                #generated_image = generated_image.resize((300, 200), Image.ANTIALIAS) #to resize the image
                generated_image.save("Generated_image.png") #save the image 
                generated_image_tk = ImageTk.PhotoImage(generated_image) #applies the image to the new window display
                generated_label = tk.Label(generate_window, image=generated_image_tk)
                generated_label.image = generated_image_tk
                generated_label.pack()

            except FileNotFoundError:
                print("Save the picture first by pressing the Save Image button.")
        else:
            print("Enter a fitness variation.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageGenerator(root)
    root.mainloop()
