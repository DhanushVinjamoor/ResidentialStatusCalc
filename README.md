
# Project Title

Development of a simple, easy to use program that reads from a set template and returns the residential status. This is developed with the Indian legal framework in mind.




## Documentation

After cloning the repo, either add your ui, or directly use the .py file.

Call the residency_liason function, with the arguments path (path to template) and ORNORrequired (whether to test ordirnary/not ordinary residency status)

Required modules:

pandas,datetime,calendar,re,collections



## Template breakdown

Each trip outside India to be given in seperate rows.

If the entire year was spent in India, set assessee category to ‘Resident’.

If PY0(refer yearcategories below) was spent fully in India, do not run the code, you were a Resident/Ordinary resident.

yearcategories:

PY0 - the previous year in question

PY1 - the year prior to the PY

PY2 - the year prior to PY1 

data required for ten such PYs

Year:

the actual year in question – mandatory for all years

startdate/enddate:

enter the start date/end date of trip(date of exit from India and entry into India)

required to be in xx/xx/xxxx format

required to be in DD/MM/YYYY format

ex. 05/04/1999

If assessee category is set to resident, any data can be entered here(but cannot be let blank)

trip categories:

syntax: destination categories – modifiers

destination categories: (only one must be chosen and maintained for the entire specific PY):

toIndia - person(Indian citizen or PIO) outside India spending time in India. toIndia and fromIndia are mutually exclusive.

fromIndia - person(Indian citizen/resident) in India spending time outside India. toIndia and fromIndia are mutually exclusive. 


modifiers to destination categories:

employment outside india

crewmember of Indian ship

citizen/PIO on visit to India

assessee categories: 

citizen/PIO/others - can only be provided for PY0 year category. One of these are mandatory. 

Resident/Non-Resident - provide this field if data is known for certain 

Unknown - provide this if unsure 

income:

mandatory for PY0

mandatory for other PY, incase assessee category has been provided as unknown

incomefromforeignsources:

leave empty if nil




