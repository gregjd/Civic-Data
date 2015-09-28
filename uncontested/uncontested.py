import csv
import glob
import json


def readAllElections(pattern='*.csv', makeCSV=True, makeJSON=False):
    """Runs the readCandidatesFile function on all CSVs in the current folder.

    Ignores CSVs that don't have the required fields (TOWN, OFFICE, DIST#).

    Args:
        pattern: (Optional) String that specifies which files to read. 
            By default, it's all files with a CSV extension.
        makeCSV: (Optional) If True, saves a CSV with the uncontested rates by 
            location for each election. Election dates are column headers and 
            each location is a row.
        makeJSON: (Optional) If True, saves a JSON file with the results ('elections_dict'). 
            File may be huge.

    Returns:
        A tuple containing:
            A dict of all the results from all the files. Election dates are keys,
                and the entire 'races' dicts (from readCandidatesFile) are the values.
            A list of dicts, with each dict representing a race and containing
                information about the race.

    Side effect:
        Saves up to two new files (CSV, JSON).
    """

    elections_dict = {}
    elections_list = []
    for file_name in glob.glob(pattern): # For each CSV in the current folder
        (races, races_list) = readCandidatesFile(file_name)
        if (races): # If the CSV didn't get skipped for not having the required fields
            elections_dict[races['date']] = races
            elections_list += races_list

    if (makeCSV):
        header = ['location'] + [e for e in sorted(elections_dict)]
        data = prepForCSV(getUncRates(elections_list), 'location')
        saveCSV('unc_rates.csv', data, header)
    if (makeJSON):
        saveJSON('elections.json', elections_dict)

    return (elections_dict, elections_list)


def readCandidatesFile(file_name, makeJSON=False):
    """Reads a CSV with candidate data and compiles a dict with the info.

    Args:
        file_name: A string file name of a CSV with data on all the 
            candidates for a given election.
        makeJSON: (Optional) If True, saves the result as a JSON file.

    Returns:
        A tuple containing:
            A dict with all the races and candidates for an election,
                as compiled by the compileCandidates function.
            A list of dicts, with each dict representing a race and containing
                information about the race.
        Returns (None, None) if the CSV doesn't have all required fields.
    """

    f = open(file_name, 'r')
    date = convertDate(getDateFromName(file_name))
    try:
        (races, races_list) = compileCandidates(csv.DictReader(f), date)
    except KeyError:
        print ("\n" + file_name + "\ndoes not have all the required fields: " +
            "'TOWN', 'OFFICE', and 'DIST#'." + "\nFile ignored.\n")
        return (None, None)
    else:
        print 'Reading:', file_name
        if (makeJSON):
            new_name = file_name.replace('.csv','.json')
            saveJSON(new_name, races) # in same directory as CSV
        return ({
            'races': races,
            'date': date,
            'unc_rates': getUncontestedRates(races)
        }, races_list)
    finally:
        f.close()


def compileCandidates(reader, date):
    """Compiles a dict of races and candidates based on raw spreadsheet data.

    Args:
        reader: A csv.DictReader with info about candidates.
        date: The str date of the election (YYYY-MM-DD).

    Returns:
        A tuple containing:
            A dict that is just like the input races except where
                each race now has a boolean field 'contested'.
            A list of dicts, where each dict represnts a race.
    """

    races = {}
    for row_ in reader:
        row = mapOffice(row_)
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
                'nonpartisan': (row['PARTY'] == 'Non-Partisan Local Office'),
                'candidates': { # 4 separate lists for the different 'DECLARATION' values
                    'Valid': [],
                    'Void': [],
                    'Withdrew': [],
                    'Under Review': []
                },
                'contested': None # later gets replaced with True/False
            }
        races[loc][o][d]['candidates'][row['DECLARATION']].append(row)
    return calculateContested(races, date)


def mapOffice(d):
    """Processes data about the office a candidate is running for.

    Cleans the office title, finds the district number, and finds the
    number of candidates you can vote for (for that office).

    Args:
        d: Dict with keys including 'TOWN', 'OFFICE', 'DIST#'.

    Returns:
        Input dict with additional keys: 'office', 'dist', 'votefor'.
    """

    def removeLastWords(text, n):
        """Removes the last n words from text."""
        
        return ' '.join(text.split(' ')[0:-n])

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


def calculateContested(races, date):
    """For each race, calculates the 'contested' field.

    Doesn't account for places where votefor is multiple but not specified.

    This function is the result of a change in the trajectory of this program.
    Originally, I had 'races' as the only export, but I later realized that
    it made more sense to use a list that could easily be filtered and
    aggregated in whatever way is desired. This function originally took
    'races', went to each race and completed a field indicating whether or not
    it's contested. I modified it to also take each race (including the answer
    to isContested, plus the date, location, office, office type, and
    district) and append it to a list of all races ('races_list').

    If I were rewriting this program from scratch, this would definitely
    be different, but for now it's not really worth refactoring this.

    Args:
        races: A dict where keys = locations, values = dicts of all the
            districts for that location.
        date: The str date of the election (YYYY-MM-DD).

    Returns:
        A tuple containing:
            A dict that is just like the input races except where
                each race now has a boolean field 'contested'.
            A list of dicts, where each dict represnts a race.
    """

    races_list = []
    for loc in races:
        for office in races[loc]:
            for district in races[loc][office]:
                d = races[loc][office][district]
                d['contested'] = isContested(d)
                other_race_info = {
                    'date': date,
                    'location': loc,
                    'office': office,
                    'office_type': getOfficeType(office),
                    'district': district
                }
                race_item = dict(d.items() + other_race_info.items())
                races_list.append(race_item)
    return (races, races_list)


def isContested(d):
    """Determines if a race is contested.

    Calculated by seeing if the number of valid candidates exceeds the number to vote for.

    Args:
        d: A dict representing a race, with keys including 'candidates', 'votefor'.

    Returns:
        A bool indicating whether or not the race is contested.
    """

    return (len(d['candidates']['Valid']) > d['votefor'])


def getOfficeType(office):
    """Parses the name of an office to figure out its type.

    Types: Executive, Legislature, School Committee, other (None).

    Args:
        office: A str name of an office, as given in the raw data.

    Returns:
        A str representing the office type.
    """

    if office in ['MAYOR', 'TOWN MODERATOR', 'GOVERNOR',
                  'PRESIDENT OF THE UNITED STATES']:
        return 'Executive'
    elif 'COUNCIL' in office:
        return 'Legislature'
    elif 'GENERAL ASSEMBLY' in office:
        return 'Legislature'
    elif 'CONGRESS' in office:
        return 'Legislature'
    elif 'SCHOOL COMMITTEE' in office:
        return 'School Committee'
    else:
        return None


### GENERAL UTILITIES


def convertDate(text):
    """Converts a string in MMDDYYYY format to YYYY-MM-DD format."""

    date = text
    y = date[4:8]
    m = date[0:2]
    d = date [2:4]
    return '-'.join([y,m,d])


def getDateFromName(file_name):
    """Takes a file name (in the formats we use) and returns the election date as a str."""

    return file_name.split('\\')[-1].split('_')[1]


def getUncontestedRates(races, printr=False):

    def getWhere(to_filter, property_, test):
        """Returns a sorted list of items where a property tests True."""

        # return sorted(filter(lambda x: (to_filter[x][property_]==test), to_filter))
        return sorted(x for x in to_filter if (to_filter[x][property_] == test))

    unc_rates = {}
    for loc in sorted(races):
        tot = 0.0
        unc = 0.0
        for office in races[loc]:
            tot += len(races[loc][office])  # How many total districts does the office have?
            unc += len(getWhere(races[loc][office], 'contested', False))
                # In how many districts were the races uncontested?
        unc_rates[loc] = {
            'tot_races': tot,
            'unc_races': unc,
            'unc_rate': (unc/tot)  # Pct of races for that location that were uncontested
        }
    if (printr):
        print 'Percent of races that were uncontested:'
        for p in sorted(unc_rates):
            print p, ' '*(16-len(p)), str((unc_rates[p][unc_rate])*100)+'%'
                # Prints the uncontested rates as percents, vertically aligned
                # >> Could use a slight adjustment in vertical alignment
    return unc_rates


### PRE-EXPORT UTILITIES


def addPropFromJSON(file_name):
    """Uses an extermal JSON file to associate properties with ____.

    Structured this way so that the file only had to be opened once.

    >>> Returns a function
    """

    f = open(file_name, 'r')
    js = json.loads(f.read())
    f.close()

    def jsonMatch(lookup):

        try:
            return js[lookup].encode('ascii')
        except KeyError:
            print lookup, 'not found in JSON file'
            return None

    return jsonMatch


def addProp(list_of_dicts, current_prop, new_prop_name, new_prop_f):
    """Takes a list of dicts and adds a new key-value pair to each one 
    based on an existing value.

    Args:
        list_of_dicts: List of dicts; each dict will have a k-v pair added
        current_prop: String key in the dicts
        new_prop_name: String key to be added to the dicts
        new_prop_f: Function that takes the value for current_prop and returns 
            the value for new_prop_name

    Returns:
        A list of dicts, each with the new property added as a k-v pair.
    """

    def propMap(x):

        new = { new_prop_name: new_prop_f(x[current_prop]) } # Creates the new k-v pair

        return dict(x.items() + new.items()) # Adds the new k-v pair to the dict

    return map(propMap, list_of_dicts)

# To-do: Rename, improve readability:
def getUncRates(races_list, group='date'):

    all_locs = {}  # Keys = unique locations
    for i in races_list:  # For each race
        if i['location'] not in all_locs:
            all_locs[i['location']] = {}
    dg = group
    for j in all_locs:  # For each location
        # loc_list = filter(lambda x: x['location']==j, races_list)
        loc_list = [x for x in races_list if (x['location']==j)]
        loc_dict = {}  # Keys = dates, values = races
        for k in loc_list:
            if k[dg] not in loc_dict:
                loc_dict[k[dg]] = []
            loc_dict[k[dg]].append(k)
        for date in loc_dict:  # For each date or date group
            unc = float(len(filter(lambda x: x['contested']==False, loc_dict[date])))
            tot = float(len(loc_dict[date]))
            all_locs[j][date] = unc/tot
    return all_locs


def getType(races_list, office_type):

    # return filter(lambda x: x['office_type'] == office_type, races_list)
    return [x for x in races_list if (x['office_type'] == office_type)]


def isPrimaryOrGeneral(elec_type):
    """Takes an election type (str) and returns whether it's a primary or general (str).

    Raises:
        Exception if 'Primary' and 'General' are both in elec_type.
    """

    if 'primary' in elec_type.lower():
        if 'general' in elec_type.lower():
            raise Exception("'Primary' and 'General' can't both be in an election type.")
        else:
            return 'Primary'
    elif 'general' in elec_type.lower():
        return 'General'
    else:
        print ('Type "' + elec_type + '" unknown.')
        return 'Unknown'


def getYearFromDate(elec_year):
    """"Extracts the year from a date in YYYY-MM-DD format."""
    # Could confirm that it's actually a year using regex, but this will work if used properly

    return elec_year[0:4]


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
                },
                {
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
        See example above for its structure. Dicts are sorted alphabetically 
        by the keys to which they used to correspond (i.e. 'PROVIDENCE').
    """

    d_list = []
    for k in sorted(d):
        d[k][key_name] = k
        d_list.append(d[k])

    return d_list


### EXPORT UTILITIES


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


if __name__ == '__main__':

    (elections_dict, elections_list) = readAllElections()

    # The following code was used for specific CSV exports:

    # for t in ['Executive', 'Legislature', 'School Committee']:
    #     header = ['location'] + [e for e in sorted(elections_dict)]
    #     data = prepForCSV(getUncRates(getType(elections_list, t)), 'location')
    #     saveCSV('unc_rates_'+t[0:3].lower()+'.csv', data, header)
    
    # header = ['location', '2006', '2008', '2010', '2012', '2014']
    # res = addProp(elections_list, 'date', 'year', getYearFromDate)
    # data = prepForCSV(getUncRates(res, 'year'), 'location')
    # saveCSV('unc_rates_by_year.csv', data, header)

    # header = ['location', 'Primary', 'General']
    # temp = addProp(elections_list, 'date', 'type_long', addPropFromJSON('list_of_elections.json'))
    # res = addProp(temp, 'type_long', 'type_short', isPrimaryOrGeneral)
    # data = prepForCSV(getUncRates(res, 'type_short'), 'location')
    # saveCSV('unc_rates_by_elec_type.csv', data, header)

    # def mapRace(race):

    #     def mapRaceFunc(x):

    #         if (x != 'candidates'):
    #             return (x, race[x])
    #         else:
    #             return (x, len(race[x]['Valid']))

    #     return dict(map(mapRaceFunc, race))

    # data = map(mapRace, elections_list)
    # header = ['date', 'location', 'office', 'office_type', 'district', 'nonpartisan',
    #     'candidates', 'votefor', 'contested']
    # # header = [contested, office, district, office_type, candidates, date, nonpartisan, votefor]
    # saveCSV('all_races.csv', data, header)