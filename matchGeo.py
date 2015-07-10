import csv

def matchGeo(match_table, voter_table):
    """
    Args:
        match_table: String name of the file with addressIDs and lat/lon coordinates
        voter_table: String name of the file with voter addresses

    Returns:
        Nothing.

    Side effect:
        Saves a CSV with all the data from voter_table plus the lat/lon coordinates 
        that correspond with each address. The file name is the same as that of 
        voter_table but with '_geocoded' appended before the '.csv' (or '.txt') extension.
    """

    vts = voter_table.split('.')
    vts.insert(1, '_geocoded.')
    new_file_name = ''.join(vts)

    f1 = open(match_table, 'r')
    reader1 = csv.DictReader(f1)
    geo_match = {}
    for row in reader1:
        geo_match[row['addressID']] = {
            'lat': row['geo_lat'],
            'lon': row['geo_lon']
        }
    f1.close()

    print '\nSaving file:', new_file_name, '...'
    with open(new_file_name, 'wb') as newfile:
        f2 = open(voter_table, 'r')
        reader2 = csv.DictReader(f2)
        header = reader2.fieldnames + ['addressID', 'geo_lat', 'geo_lon']
        writer = csv.DictWriter(newfile, header)
        writer.writeheader()
        for row in reader2:
            address = ', '.join([row['STREET_NUMBER'], row['STREET_NAME1'], row['CITY'], row['STATE']])
            row['addressID'] = address
            row['geo_lat'] = geo_match[address]['lat']
            row['geo_lon'] = geo_match[address]['lon']
            writer.writerow(row)
        f2.close()
    newfile.close()
    print 'Saved file:', new_file_name
