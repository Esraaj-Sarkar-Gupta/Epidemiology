import numpy as np
import time as tm
import os as os
import matplotlib as mpl
import matplotlib.pyplot as plt


try:
    os.makedirs('./Logs')
except:
    pass

T = tm.localtime()
filename = f"Logs/Logs_{T[7]}_{T[3]}-{T[4]}-{T[5]}.txt" # Set log file name

def log_display(text):
    with open(filename , 'a') as log_file:
        log_file.write(f"\n{T[7]} - {T[3]}:{T[4]}:{T[5]} > {text}\n")
    print(f"{T[3]}:{T[4]}:{T[5]} > {text}")
def log(text):
    with open(filename , 'a') as log_file:
        log_file.write(f"\n{T[7]} - {T[3]}:{T[4]}:{T[5]} > {text}\n")
        
def mag(x,y):
    return np.sqrt(x**2 + y**2)
        

boundary = 100

virulence = 100

infectiousness = 1
transmissibility = 1

transmission_threshold = 0.60

decay_constant = 0.005 # Constant for viral clearance

log(f"Initial Parameters:\nBound:{boundary},Virulence:{virulence},Infectiousness:{infectiousness},Transmissibility:{transmissibility},Transmission_Threshold:{transmission_threshold},Decay_Constant:{decay_constant}")

number_of_elements = int(input("Number of elements: "))
number_of_steps = int(input("Number of steps: "))

log(f"Number of Elements: {number_of_elements}; Number of Steps: {number_of_steps}")

class particle():
    def __init__(self, X, Y, viral_load, status):
        self.X = X
        self.Y = Y
        self.viral_load = viral_load
        self.status = status
        
    def update_pos(self, add_X, add_Y): # Update the positions of the element as a result of random walk
        self.X += add_X
        self.Y += add_Y
        
        if self.X > boundary:
            self.X = boundary
        if self.Y > boundary:
            self.Y = boundary
    
    def viral_decay(self): # Update properties based on the phenomenon of viral decay
        log(f"Reduced viral load of {self} by {self.viral_load * (1 - decay_constant)}")      
        self.viral_load = self.viral_load * (1 - decay_constant) # Y = Y - Y * k, induces exponential decay in viral_load
    
    def infection(self, body):
        probability = body.viral_load * transmissibility * np.random.rand() # Probability of transmission
        probability = min(probability, 1) # Ensure probability does not exceed 1
        
        if probability >= transmission_threshold:
            delta = body.viral_load * infectiousness * np.random.rand()
            self.viral_load += delta # Viral load increases as a function of several variables
            log(f"Infection of {self} and {body} gives probability P = {probability} -> Viral load of {self} increased by {delta}")
        else:
            log(f"Infection of {self} and {body} gives probability P = {probability} -> P less than threshold {transmission_threshold}")
            
    def housekeeper(self):
        # Update status based on viral_load
        if self.viral_load < 0.5 * virulence:
            self.status = 'susceptable'
        else:
            self.status = 'infected'
        
        # Check for positional bounds
        if self.X > boundary:
            self.X = boundary
        if self.Y > boundary:
            self.Y = boundary
            
    def color(self):
        if self.status == "infected":
            return 'red'
        elif self.status == 'susceptable':
            return 'blue'
            
        
# Initialise elements    

bottom_vl_limit = 0
top_vl_limit = 10
log("Random viral_load assignment limit:{bottom_vl_limit} > {top_vl_limit}")     

elements = []

susceptible_count = []
infected_count = []

for _ in range(number_of_elements):
    elements.append(particle(np.random.uniform(-boundary, boundary),
                             np.random.uniform(-boundary, boundary),
                             np.random.uniform(bottom_vl_limit, top_vl_limit),
                             "unassigned"))
elements.append(particle(np.random.uniform(-boundary, boundary),
                         np.random.uniform(-boundary, boundary),
                         100,
                         'unassigned'))
    
for body in elements: # Run housekeeper function for every body
    body.housekeeper()
    
log_display(f"{len(elements)} elements have been initialised. ")

def count(element_list):
    susceptable_count, infected_count = 0, 0
    for element in element_list:
        if element.status == 'susceptable':
            susceptable_count += 1
        elif element.status == 'infected':
            infected_count += 1
    #print(f"Safe: {safe}\nCarrier: {carrier}\nInfected: {infected}\nSeverely Infected: {severely_infected}\nUncategorised: {uncat}")
    return susceptable_count, infected_count

def plot(element_list, t):
    plt.figure(figsize=(10,10))
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title(f"System at instance {t}")
    plt.xlim(-boundary, boundary)
    plt.ylim(-boundary, boundary)
    
    for element in element_list:
        plt.scatter(element.X,
                    element.Y,
                    color = element.color(),
                    s = 40)
    plt.grid(True)
    plt.show()

# Function to update the positions of elements in element_list using a random walk    
def update_position(element_list, radius): 
    for element in element_list:
        angle = np.random.uniform(0, 2 * np.pi) # Chose a random angle between 0 and 2pi
        element.update_pos(radius * np.cos(angle), radius * np.sin(angle)) # Advance in the angle by a radius 

def check_contact(element_list, contact_radius):
    bodies_in_contact = []
    for i in range(len(element_list)):
        for j in range(i, len(element_list)):
            primary_element = element_list[i]
            secondary_element = element_list[j]
            
            if primary_element == secondary_element:
                continue
            
            delta_distance = mag(primary_element.X - secondary_element.X, primary_element.Y - secondary_element.Y)
            if delta_distance < contact_radius:
                bodies_in_contact.append((primary_element, secondary_element))
    return bodies_in_contact                     

def update_contact(contact_list):
    for couple in contact_list:
        couple[0].infection(couple[1])
        couple[1].infection(couple[0])
    
# Define list to ho      
def update(t):
    for t in range(t):
        update_position(elements, 1) # Update the positions of the elements by a distance 
        plot(elements, t) # Plot the updated positions of the elements
    
        number_susceptible, number_infected = count(elements)
       
        susceptible_count.append(number_susceptible)
        infected_count.append(number_infected)
            
        contact_list = check_contact(elements, 1) # Check for contacts between two elements
        if len(contact_list) != 0:
            log_display(f"Number of contacts at instance: {t} : {len(contact_list)}")
        else:
            log(f"Number of contacts at instance: {t} : {len(contact_list)}")
        #print(f"Contacts at {t}: {len(contact_list)}")
        update_contact(contact_list)
        
        for element in elements:
            element.housekeeper()
            element.viral_decay()
        
        
        
update(number_of_steps)

plt.figure(figsize=(10,10))
plt.title("Evolution of System")

plt.xlabel("Instances")
plt.ylabel("Count")


plt.plot(range(number_of_steps), susceptible_count, color = 'blue')
plt.plot(range(number_of_steps), infected_count, color = 'red')

print(susceptible_count)
print(infected_count)

plt.grid(True)
plt.show()

log(f"Safe, carrier, infected, severely_infected, uncategorised: ")
log(susceptible_count)
log(infected_count)


log_display('End')