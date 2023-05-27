# module to test and return residency status based on inputs
# if there are multiple dates, use the template to input data and calculate
import datetime


# Main function, hook onto this function to handle all classes and methods
def residency_liason(path=None, ORNORrequired=True, filedeclared=True):
    # create an instance of residency handler class
    handler = individual_residencytests(filedeclared, path, ORNORrequired)

    # method to access the file, and error handler for errors
    handler.setupfilelisaon()
    if handler.filetest is True:
        valuefinal = handler.mainhandler()  # start processing data
        if valuefinal == 'Error:template not filled':
            return valuefinal
        else:
            return valuefinal  # if no errors, returns output as a tuple of (BOOL=Resident/Not Resident,BOOL=Ordinary
            # ,Not Ordinary")
    else:
        return handler.filetest  # return error in file opening


class individual_residencytests:

    def __init__(self, filedeclared=True, path=None, ORNORrequired=True):
        self.PYdaysinIndia = None
        self.filetest = None
        self.file_handler = None
        self.filedeclared = filedeclared

        # Todo bring in validation for filepath and name
        self.path = "Templates\\residency_template.csv" if path is None else path

        self.ORNORrequired = ORNORrequired

        self.PY0daysinIndia = None

    def setupfilelisaon(self):

        # set up an instance of subclass filehandler
        self.file_handler = filehandler(self.path)
        if self.file_handler.getcsvdata():
            self.filetest = True
        else:
            self.filetest = 'Error in retrieving file'

    def mainhandler(self):

        # call method to get data from csv, and if no data is filled raise error
        try:
            PY0data = self.file_handler.get_specific_data('PY0')
        except:
            return 'Error:template not filled'

        # begin testing conditions to determine Residency status
        if self.Sec6_1_handler(PY0data):
            # begin testing for Ordinary, Not ordinary resident
            if self.sec_6_6_ORNORtest(PY0data):
                return True, True
            else:
                return True, False
        else:
            return False, False

    def Sec6_1_handler(self, PY0data, index=0, last_PY=10):

        # Index argument is needed for when this method is called from ORNOR method, same for last_PY
        # (required in cases where data less than 10 years provided)
        if self.Sec6_1_a_test(PY0data[3], year=PY0data[0][0], daysoutstart=PY0data[1],
                              daysoutend=PY0data[2]):
            return True
        else:
            if self.sec6_1_b_test(PY0data[4], PY0data[6], PY0data[7], index, last_PY):
                return True
            else:
                return False

    def Sec6_1_a_test(self, modifier, year=datetime.datetime.now().year, daysoutstart=(), daysoutend=(),
                      ):

        # condition 1 test:

        if modifier == 'fromIndia':
            self.PYdaysinIndia = self.dayscalc_citizenPIO_basedondaysout(daysoutstart, daysoutend, AY=year)
        else:
            self.PYdaysinIndia = self.dayscalc_citizenPIO_basedondaysin(daysoutstart, daysoutend)

        if self.PYdaysinIndia >= 182:
            return True
        else:
            return False

    def sec6_1_b_test(self, tripcategories, gti, incomefromforeignsources, index=0, last_PY=10):
        threshold_2 = 60
        eligibletrips = ('employment outside india', 'crewmember of Indian ship', 'citizen/PIO on visit to India')
        # todo insert method for ship trip start and end date based on certificate

        for trips in tripcategories:
            if trips in eligibletrips:
                if (gti[0] - incomefromforeignsources[0]) <= 1500000:
                    threshold_2 = 182
                else:
                    threshold_2 = 120
                    break

        if not self.PYdaysinIndia >= threshold_2:
            return False
        else:
            cumulativedays = 0

            for years in range(index, index + 4):

                # test to ensure potential index is not higher than last possible PY provided by user
                if years > last_PY:
                    return False

                dataset = eval('self.file_handler.get_specific_data("PY' + str(years) + '")')
                if dataset[3][0] == 'fromIndia':
                    PYdaysinIndia = self.dayscalc_citizenPIO_basedondaysout(dataset[1], dataset[2], dataset[1][0]
                                                                            )
                else:
                    PYdaysinIndia = self.dayscalc_citizenPIO_basedondaysin(dataset[1], dataset[2],
                                                                           )
                cumulativedays = cumulativedays + PYdaysinIndia

                # test for condition
                if cumulativedays >= 365:
                    return True

            # if condition not met in loop, condition is failed
            return False

    def sec_6_6_ORNORtest(self, PY0data):

        # test for condition (b)
        if self.PYdaysinIndia >= 182 and ('citizen' in PY0data[5] or 'PIO' in PY0data[5]):
            if (PY0data[6][0] - PY0data[7][0]) > 1500000:
                return True
        else:
            # call method to get a sorted list of assessee status, with duplicates removed.Returns a tuple with
            # 0:counter 1:list
            inputdata = self.file_handler.getstatusdata()
            dataset = inputdata[0]

            # create a function to return a list of all values ending with a selected modifier.
            # Required because there are multiple potential status conditions attached to a specific modifier

            result = lambda targetstr: [value for key, value in dataset.items() if key.endswith(targetstr)]

            non_residentcount = sum(result('Non-Resident'))
            unknowncount = sum(result('Unknown'))
            lastyear = self.file_handler.getlastPY()
            residentcount = lastyear - non_residentcount - unknowncount

            if residentcount >= 2:

                # identify end of range based on last PY entered by the user
                last_year_condition2 = lastyear if lastyear <= 8 else 8
                allPY = ['PY' + str(x) for x in range(1, last_year_condition2)]
                cumulativedays = 0

                # create a loop to test each of the PY in  question for number of days in India, and test condition
                for count, targetyears in enumerate(allPY):
                    dataset = eval('self.file_handler.get_specific_data("' + str(targetyears) + '")')
                    if dataset[3][0] == 'fromIndia':
                        PYdaysinIndia = self.dayscalc_citizenPIO_basedondaysout(dataset[1], dataset[2], dataset[1][0]
                                                                                )
                    else:
                        PYdaysinIndia = self.dayscalc_citizenPIO_basedondaysin(dataset[1], dataset[2],
                                                                               )
                    cumulativedays = cumulativedays + PYdaysinIndia
                    if cumulativedays >= 730:
                        return True
                return False

            else:
                if not (residentcount + unknowncount) >= 2:
                    return False
                else:

                    # get a list of indices where modifier set to Unknown based on sorted list.
                    # Requires user input to be in order too.
                    unknown_indices = [i for i, x in enumerate(inputdata[1]) if "Unknown" in x]

                    # call the baseresidency handler method for all instances above and test for residency
                    for indices in unknown_indices:
                        dataset_ORNOR = eval('self.file_handler.get_specific_data("PY' + str(indices) + '")')
                        if self.Sec6_1_handler(dataset_ORNOR, indices, lastyear):
                            residentcount += 1
                        if residentcount >= 2:
                            break

                    if not residentcount >= 2:
                        return False
                    else:

                        # Refer above for first IF condition above for explanations

                        last_year_condition2 = lastyear if lastyear <= 8 else 8
                        allPY = ['PY' + str(x) for x in range(1, last_year_condition2)]
                        cumulativedays = 0

                        for count, targetyears in enumerate(allPY):
                            dataset = eval('self.file_handler.get_specific_data("' + str(targetyears) + '")')
                            if dataset[3][0] == 'fromIndia':
                                PYdaysinIndia = self.dayscalc_citizenPIO_basedondaysout(dataset[1], dataset[2],
                                                                                        dataset[1][0]
                                                                                        )
                            else:
                                PYdaysinIndia = self.dayscalc_citizenPIO_basedondaysin(dataset[1], dataset[2],
                                                                                       )
                            cumulativedays = cumulativedays + PYdaysinIndia
                            if cumulativedays >= 730:
                                return True
                        return False

    # other miscellaneous functions
    def dayscalc_citizenPIO_basedondaysout(self, PYdaysoutstart=(), PYdaysoutend=(),
                                           AY=datetime.datetime.now().year):
        # This method is to be called if you need to calculate time spent based on the
        # assumption that the data provided is the time spent outside India

        # check if arguments are empty
        if not PYdaysoutstart or not PYdaysoutend:
            return 'No data provided'
        else:
            total_days = self.days_in_year(AY)
            tripdays = []

            for count, trips in enumerate(PYdaysoutend):
                from datetime import datetime

                # required date entered to be in dd/mm/yyyy format, or else an error will be raised

                date_format = "%d/%m/%Y"
                a = datetime.strptime(PYdaysoutstart[count], date_format)
                b = datetime.strptime(PYdaysoutend[count], date_format)

                delta = b - a

                tripdays.append(delta.days + 1)

            timeinIndia = total_days - sum(tripdays)

            return timeinIndia

    @staticmethod
    def dayscalc_citizenPIO_basedondaysin(PYdaysintstart=(), PYdaysinend=(),
                                          ):

        # check if arguments are empty
        if not PYdaysintstart or not PYdaysinend:
            return 'No data provided'
            # todo insert error handler in all handler methods
        else:
            tripdays = []

            for count, trips in enumerate(PYdaysinend):
                from datetime import datetime
                date_format = "%d/%m/%Y"
                a = datetime.strptime(PYdaysintstart[count], date_format)
                b = datetime.strptime(PYdaysinend[count], date_format)

                delta = b - a
                if delta.days > 366:
                    return 'Error:trip longer than 1 year entered!'
                tripdays.append(delta.days + 1)

            return sum(tripdays)

    @staticmethod
    def days_in_year(year):

        # get number of days in a given FY. year argument provided must be the year in which the ending March falles on
        # for example for FY 22-23 the argument must be 2023

        year = int(year)
        from calendar import monthrange
        finalcount = []
        for month in range(4, 16):
            if month <= 12:
                finalcount.append(monthrange(year - 1, month)[1])
            else:
                finalcount.append(monthrange(year, month - 12)[1])

        return sum(finalcount)


class filehandler:

    def __init__(self, path):
        self.df = None
        self.path = path

    def getcsvdata(self):
        import pandas as pd
        try:
            self.df = pd.read_csv(self.path)
            return True
        except:
            return False

    def get_specific_data(self, index):
        """

        :type index: str
        """

        # function to return a nested list of each column of dataframe for a specific PY - i.e to return the row for
        # a given PY
        returnval = []
        mask = self.df['yearcategories'].values == index  # create mask to use filter data
        returnval.append(self.df.loc[mask, 'year'].tolist())

        # these data are required to be in a tuple
        returnval.append(self.convert(self.df.loc[mask, 'startdate'].tolist()))
        returnval.append(self.convert(self.df.loc[mask, 'enddate'].tolist()))

        # splitting the trip categories into destination and modifiers, in order to identify if eligible in functions
        # which need it
        from re import split
        destinations = []
        modifiers = []

        for splititems in self.df.loc[mask, 'tripcategories'].tolist():
            splitr = split('-', splititems)
            destinations.append(splitr[0])
            modifiers.append(splitr[1])

        returnval.append(destinations)
        returnval.append(modifiers)

        returnval.append(self.df.loc[mask, 'assesseecategories'].tolist())
        returnval.append(self.df.loc[mask, 'income'].tolist())
        returnval.append(self.df.loc[mask, 'incomefromforeignsources'].tolist())

        return returnval

    def getstatusdata(self):

        input_PY_list = [*set(self.df['yearcategories'].tolist())]  # remove duplicates by converting to a set format
        # above statement returns a jumbled list, the below block of code sorts it chronologically

        returnval = []
        input_PY_list = sorted(input_PY_list)

        # run a loop to get assessee categories for each PY(based on the PY list without duplicates extracted above)
        for PYears in input_PY_list:
            mask = self.df['yearcategories'].values == PYears
            value = self.df.loc[mask, 'assesseecategories'].tolist()
            returnval.append(value[0])

        # prepare a count of each element in the list generated above
        from collections import Counter
        dataset = Counter(returnval)

        # return both, as they are utilised in determining the condition applicability, and to use in the loop utilised
        # to test condition2 in OR NOR testing
        return dataset, returnval

    def getlastPY(self):

        # get the last PY chronologically, not based on order of user input

        PY_list = self.df['yearcategories']
        sorted_PY_list = []
        from re import split
        for items in self.alphanumericsort(PY_list):
            sorted_PY_list.append(items)
        # extract the last value and get the year code
        lastval = split("([0-9]+)", sorted_PY_list[-1])

        last_year = 0

        # get the integer value of last year entered by user
        for splitvalues in lastval:
            try:
                last_year = int(splitvalues)
            except:
                continue
        return last_year

    def alphanumericsort(self, targetword):
        # uses Jeff Atwood's sorting algorithm
        from re import split
        convert = lambda text: int(text) if text.isdigit() else text
        alphanum_key = lambda key: [convert(c) for c in split("([0-9]+)", key)]
        return sorted(targetword, key=alphanum_key)

    @staticmethod
    def convert(targetlist):
        return tuple(targetlist)

    def clean_year(self, year):

        year = int(year)
        if year < 1947:
            return False
        else:
            return True


#classhandler = residency_liason()
#print(classhandler)
# print(classhandler.days_in_year(2023))
"""classhandler = filehandler("Templates\\residency_template.csv")
classhandler.getcsvdata()
print(classhandler.getlastPY())

print(classhandler.getstatusdata())
#print(residency_liason())
inputdata=classhandler.getstatusdata()
from collections import Counter
datacounts=Counter(inputdata)
print(datacounts)"""
