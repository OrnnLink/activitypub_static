import os
from plantuml import PlantUML

# Define the sequence diagram in PlantUML format
diagram = """
@startuml
actor User
participant "ActivityController" as A
participant "ResourceHandler" as B
participant "UserHandler" as C

User -> A: Request to create WebFinger
A -> B: Verify if user exists
B --> A: User exists? No -> Create user, return True Yes -> Return False
A -> C: Verify if cache exists for new user
C --> A: Cache exists? No -> Create cache, return True Yes -> Return False
A --> User: Return success or failure
@enduml
"""


#B --> A: Response from B
#A --> User: Response from A
# Save the diagram definition to a file
# participant "ActivityHandler" as D
with open("sequence_diagram.txt", "w") as file:
    file.write(diagram)

# Use PlantUML to generate the diagram from the text file
plantuml = PlantUML(url='http://www.plantuml.com/plantuml/img/')

try:
    plantuml.processes_file("sequence_diagram.txt")
except Exception as e:
    print(e)

# Now the diagram will be generated and saved as a PNG file

