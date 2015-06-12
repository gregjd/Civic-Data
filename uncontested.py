import csv
import glob
import json


### Maybe somehow unpack individual races? Would make filtering easier.

def aggregateByLocation(elections, k, f):
    """
    """

    locs = {}
    for date in elections:
        if k in elections[date]:
            for loc in elections[date][k]:
                if loc not in locs:
                    locs[loc] = {}
                # if date not in locs[loc]:
                #     locs[loc][date] = None
                locs[loc][date] = f(elections[date][k][loc])
        else:
            raise Exception("'k' must be either 'races' or 'unc_rates'.")

    return locs

## Could make it a more generic combine function
def combineElections(data, types, combine=None):
    """
    Args:
        data: Dict with data for one or more elections
        types: Dict where keys = election dates (YYYY-MM-DD), values = attributes
        combine: (Optional) ______ that gives rules for grouping multiple types
    
    Returns:
        A dict where keys = types, values = the elections included
    """

    # Will only handle elections that are both in data and types

    # Will need to do more here....

    return

def aggregatePrimaryGeneral(___):

    return

def prepForCSV(d, key_name):
    """Turns a dict of dicts into a list of dicts ready for saving to CSV.

    Example:
        Input:
            key_name = 'location'
            d = {
                'PROVIDENCE': {
                    '2014-09-09': 0.22,
                    '2014-11-04': 0.56
                },
                'CRANSTON': {
                    '2014-09-09': 0.24,
                    '2014-11-04': 0.29
                }
            }
        Output:
            [
                {
                    'location': 'CRANSTON',
                    '2014-09-09': 0.24,
                    '2014-11-04': 0.29
                }, {
                    'location': 'PROVIDENCE',
                    '2014-09-09': 0.22,
                    '2014-11-04': 0.56
                }
            ]

    Args:
        d: Dict where keys = some identifying name/ID, values = dicts of data 
            where keys = the fields that will be columns in the CSV, values = data.
        key_name: String name for the column in the CSV that will correspond to 
            the keys in d.

    Returns: A list of dicts, with each dict intended to be a row in the CSV.
        See example above for its structure.
    """

    d_list = []
    for k in sorted(d):
        d[k][key_name] = k
        d_list.append(d[k])

    return d_list

def saveCSV(new_file_name, data, header):
    """Takes a list of dicts and saves the result as a CSV.

    Args:
        new_file_name: String name of the new file.
        data: Dict/list where keys = location names, values = sub-dicts where:
            keys = elections/election groups, values = uncontested rates.
            >>>>> change
        header: List that will form the header row of the CSV.
            Note that the first item (header[0]) will be the column name for
            the leftmost column - probably 'location'.

    Returns:
        Nothing.

    Side effect:
        Saves a new file (CSV).
    """

    print '\nSaving file:', new_file_name, '...'
    with open(new_file_name, 'wb') as csvfile:
        writer = csv.DictWriter(csvfile, header)
        writer.writeheader()
        for d in data:
            writer.writerow(d)
    csvfile.close()
    print 'Saved file:', new_file_name

    return



def readAllElections(pattern='*.csv', makeCSV=True, makeJSON=False):
    """Runs the readCandidatesFile function on all CSVs in the current folder.

    Ignores CSVs that don't have the required fields (TOWN, OFFICE, DIST#).

    Args:
        pattern: (Optional) String that specifies which files to read. 
            By default, it's all files with a CSV extension.
        makeCSV: (Optional) If True, saves a CSV with the uncontested rates by 
            location for each election. Election dates are column headers and 
            each location is a row.
        makeJSON: (Optional) If True, saves a JSON file with the results ('elections'). 
            File may be huge.

    Returns:
        A dict of all the results from all the files. Election dates are keys, 
        and the entire 'races' dicts (from readCandidatesFile) are the values.

    Side effect:
        Saves up to two new files (CSV, JSON).
    """

    elections = {}
    # all_locations = set()
    all_locations = {}
    for file_name in glob.glob(pattern): # For each CSV in the current folder
        # date = convertDate(getDateFromName(file_name))
        races = readCandidatesFile(file_name)
        if (races): # If the CSV didn't get skipped for not having the required fields
            elections[races['date']] = races

            for place in elections[races['date']]['races']:
                if place not in all_locations:
                    # all_locations.add(place)
                    all_locations[place] = {'location': place}

    if (makeCSV): # Breaking out as a separate function for aggregation!
        # csv_name = 'unc_rates.csv'
        # print '\nSaving file:', csv_name, '...'
        # with open(csv_name, 'wb') as csvfile:
        #     # field_names = ['date'] + [p for p in sorted(all_locations)]
        #     # writer = csv.DictWriter(csvfile, field_names)
        #     # writer.writeheader()
        #     # for e in sorted(elections):
        #     #     e_dict = elections[e]['unc_rates']
        #     #     e_dict['date'] = e
        #     #     writer.writerow(e_dict)

        #     fields = ['location'] + [e for e in sorted(elections)] # Dates as column headers
        #     # print fields
        #     writer = csv.DictWriter(csvfile, fields)
        #     writer.writeheader()
        #     for p in sorted(all_locations): # For each location
        #         p_dict = {} # Dict will be used to write to CSV (keys = CSV header fields)
        #         p_dict['location'] = p
        #         for e in elections: # For each election date
        #             if p in elections[e]['races']:
        #                 p_dict[e] = elections[e]['unc_rates'][p]['unc_rate']
        #         writer.writerow(p_dict)
        # csvfile.close()
        # print 'Saved file:', csv_name

        header = ['location'] + [e for e in sorted(elections)]
        data = []
        for p in sorted(all_locations):
            for e in elections:
                if p in elections[e]['unc_rates']:
                    all_locations[p][e] = elections[e]['unc_rates'][p]['unc_rate']
            data.append(all_locations[p])

        saveCSV('unc_rates.csv', data, header)

    if (makeJSON):
        saveJSON('elections.json', elections)

    return elections

def readCandidatesFile(file_name, makeJSON=False):
    """Reads a CSV with candidate data and compiles a dict with the info.

    Args:
        file_name: A string file name of a CSV with data on all the 
            candidates for a given election.
        makeJSON: (Optional) If True, saves the result as a JSON file.

    Returns:
        A dict with all the races and candidates for an election,
        as compiled by the compileCandidates function.
        Returns None if the CSV doesn't have all required fields.
    """

    f = open(file_name, 'r')
    try:
        races = compileCandidates(csv.DictReader(f))
    except KeyError:
        print ("\n" + file_name + "\ndoes not have all the required fields: " +
            "'TOWN', 'OFFICE', and 'DIST#'." + "\nFile ignored.\n")
        return None
    else:
        print 'Reading:', file_name
        if (makeJSON):
            new_name = file_name.replace('.csv','.json')
            saveJSON(new_name, races) # in same directory as CSV
        return {
            'races': races,
            'date': convertDate(getDateFromName(file_name)),
            'unc_rates': getUncontestedRates(races)
        }
    finally:
        f.close()
    

def compileCandidates(reader):
    """Compiles a dict of races and candidates based on raw spreadsheet data.

    Args:
        reader: A csv.DictReader with info about candidates.

    Returns:
        A dict with all the races and candidates.
        Keys are locations (municipality names, state, or federal), 
        values are dicts with keys being office names and values being
        dicts with keys being district numbers and values being dicts with 
        information regarding a specific race: list of candidates, how many you 
        could vote for, whether or not the race was contested, and whether 
        or not the race was nonpartisan.
    """

    races = {}

    for row in reader:
        row = mapOffice(row)
        loc = findLocation(row)
        o = row['office']
        d = row['dist']
        if loc not in races: # if location is not in election's list of locations
            races[loc] = {}
        if o not in races[loc]: # if office is not in location's list of offices
            races[loc][o] = {}
        if d not in races[loc][o]: # if district is not already in office's list of districts
            races[loc][o][d] = {
                'votefor': int(row['votefor']),
                'nonpartisan': (row['PARTY']=='Non-Partisan Local Office'),
                'candidates': { # 4 separate lists for the different 'DECLARATION' values
                    'Valid': [],
                    'Void': [],
                    'Withdrew': [],
                    'Under Review': []
                },
                'contested': None # later gets replaced with True/False
            }
        races[loc][o][d]['candidates'][row['DECLARATION']].append(row)

    return calculateContested(races)


def mapOffice(d):
    """Processes data about the office a candidate is running for.

    Cleans the office title, finds the district number, and finds the
    number of candidates you can vote for (for that office).

    Args:
        d: Dict with keys including 'TOWN', 'OFFICE', 'DIST#'.

    Returns:
        Input dict with additional keys: 'office', 'dist', 'votefor'.
    """

    # Some of these operations could be replaced with regex, but they also work fine as-is

    o = d['OFFICE']
    
    # 'votefor': the number of candidates you're supposed to vote for
    # default is 1; overridden if office title says 'VOTE FOR #' at the end
    if o.split()[-3:-1] == ['VOTE','FOR']:
        d['votefor'] = o.split()[-1]
        o = removeLastWords(o,3)
    else:
        d['votefor'] = 1
    
    # 'dist': the district number
    # default is the number in the DIST# field; overriden if given in office title
    if ((o.split()[-2:-1] == ['DISTRICT']) and (o.split()[-1] != 'COMMITTEE')):
        d['dist'] = o.split()[-1]
        o = removeLastWords(o,2)
    else:
        d['dist'] = d['DIST#']

    # 'office': the name of the office the candidate is running for (minus extraneous info)
    delete = ['WITHOUT PARTY MARKS OR DESIGNATION', 'NON PARTISAN ', 'NON-PARTISAN ']
    for i in delete:
        o = o.replace(i,'')
    d['office'] = o

    return d


def findLocation(d):
    """Finds the location of the race.

    Args:
        d: Dict with details about an office (keys include: 'office', 'dist', 'CITY').

    Returns:
        A string of the location of the race (federal, state, municipality name).
    """

    for i in ['IN CONGRESS', 'PRESIDENTIAL ELECTOR', 
        'PRESIDENT OF THE UNITED STATES', 'DELEGATE FOR']:
        if i in d['office']:
            return 'federal'
    for j in ['STATE COMMITTEE', 'DISTRICT COMMITTEE', 'IN GENERAL ASSEMBLY']:
        if j in d['office']:
            return 'state'
    if 'Statewide' in d['dist']:
        return 'state'
    return d['CITY'] # default: assume location is municipality


def calculateContested(races):
    """For each race, calculates the 'contested' field."""
    # Doesn't account for places where votefor is multiple but not specified
    for loc in races:
        for office in races[loc]:
            for district in races[loc][office]:
                d = races[loc][office][district]
                d['contested'] = isContested(d)

    return races


def isContested(d):
    """Determines if a race is contested.

    Calculated by seeing if the number of valid candidates exceeds the number to vote for.

    Args:
        d: A dict representing a race, with keys including 'candidates', 'votefor'.

    Returns:
        A bool indicating whether or not the race is contested.
    """

    return (len(d['candidates']['Valid']) > d['votefor'])


def saveJSON(new_file_name, data):
    """Saves data as JSON at new_file_name.

    Args:
        new_file_name: String name of the file to be created.
        data: The data. Probably a dict.

    Returns:
        Nothing.

    Side effect:
        Saves a new file (JSON).
    """

    print '\nSaving file:', new_file_name, '...'
    
    nf = open(new_file_name, 'w')
    json.dump(data, nf, indent=4, sort_keys=True)
    nf.close()

    print 'Saved file:', new_file_name
    
    return


def removeLastWords(text, n):
    """Removes the last n words from text."""
    
    return ' '.join(text.split(' ')[0:-n])


def getDateFromName(file_name):
    """Takes a file name (in the formats we use) and returns the election date as a str."""

    return file_name.split('\\')[-1].split('_')[1]


def convertDate(text):
    """Converts a string in MMDDYYYY format to YYYY-MM-DD format."""

    date = text
    y = date[4:8]
    m = date[0:2]
    d = date [2:4]
    return '-'.join([y,m,d])


## Do I really need this? Could I just include it in getUncontestedRaces?
def getWhere(to_filter, property_, boolean):
    return sorted(filter(lambda x: (to_filter[x][property_]==boolean), to_filter))


def getUncontestedRates(races, printr=False):

    unc_rates = {}
    for loc in sorted(races):
        tot = 0.0
        unc = 0.0
        for office in races[loc]:
            tot += len(races[loc][office]) # How many total districts does the office have?
            unc += len(getWhere(races[loc][office], 'contested', False))
                # In how many districts were the races uncontested?
        unc_rates[loc] = {
            'tot_races': tot,
            'unc_races': unc,
            'unc_rate': (unc/tot) # Pct of races for that location that were uncontested
        }

    if (printr):
        print 'Percent of races that were uncontested:'
        for p in sorted(unc_rates):
            print p, ' '*(16-len(p)), str((unc_rates[p][unc_rate])*100)+'%'
                # Prints the uncontested rates as percents, vertically aligned
                # >>>>>>> Could use a slight adjustment in vertical alignment

    return unc_rates



if __name__ == '__main__':

    elections = readAllElections()
    someDict = aggregateByLocation(elections, 'unc_rates', (lambda x: x['unc_rate']))
