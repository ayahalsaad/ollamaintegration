from langchain.prompts import PromptTemplate

fields_to_extract = [
   #  "What is the title for this Service Bulletin (SB), usually the title comes after a specific airplane part name, its located in the first couple of pages.",
    "what is the Aircraft type from the 'Effectivity' section of the SB.",
   #  "ATA Chapter and Section",
   #  "EO Nature",
   #  "References",
   #  "Reason / Description",
   #  "Concurrent Requirements",
   #  "Classification",
   #  "Manpower",
   #  "Weight and Balance / Electrical Load Data / Publication Affected",
   #  "Zones",
   #  "Notes to Planning",
   #  "Material Information",
   #  "Accomplishment Instructions"
]

prompt_template = PromptTemplate(
    input_variables=["text", "fields"],
    template="""
    You are an expert flight engineer tasked with extracting specific information from a Service Bulletin (SB) document.
Below is the relevant text from the SB:
{text}
You are tasked to extract the following field: {fields}
DO NOT FORGET : Return ONLY the extracted value for the field in a dictionary format. 
"""
)

