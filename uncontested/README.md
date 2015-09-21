uncontested.py
===

The program determines which Rhode Island electoral races (at local, state, and federal levels) were contested vs. uncontested, and can calculate summary statistics.

It takes as input candidate information files obtained from the Rhode Island Secretary of State's office; these files contain public information that candidates submitted when they declared candidacy, as well as state-added ddata (such as whether or not a candidate ended up winning the race). There are two outputs: a list of dictionaries (with each dictionary containing information about a particular race) and a dictionary of dictionaries (many levels deep, which has been organized in a way that makes it easily readable when exported to JSON).

The program can export data as CSV and JSON files. The CSV exports are summary data, typically showing the percent of races that were uncontested broken down by a location (municipality, council district) and another dimension (year, primary vs. general), and optionally filtered by a type of race (executive office, legislature, school committee). The JSON exports are of the candidate data.

There are several challenges this program addresses:

* One of the biggest is it determines what level of government and office a candidate was running for. The source data has fields for office and district, but these can overlap. Meaning, you might have an office of "CITY COUNCIL" and a district of "2" but candidates might be running in several different cities that have a city council district 2. In this case, we would need to check the municipality field and then assign these candidates to races on separate city councils. But candidates for the state legislature and US House of Representatives will also have district numbers, and in these cases the candidates will need to be assigned to a location of "state" or "federal" (as appropriate) with the district falling within that, as they are governing bodies that exist at the state/federal level instead of a local level.
* Additionally, the office name field sometimes contains information that is actuallty district information. For example, a candidate might have an office of "CITY COUNCIL DISTRICT 2" with no district listed, and this will need to be converted to an office of "CITY COUNCIL" and district of 2. The office field also sometimes contains extraneous information that needs to be stripped out.
* In some races, voters can vote for multiple candidates and multiple candidates are allowed to win. This is common for school committee elections. This program will extract "vote-for" information from the office title (such as "SCHOOL COMMITTEE VOTE FOR 5") and put it in a separate field, to be used when determining whether or not a race is contested.
* The candidate data contains information for everyone who declared a candidacy. Most people ended up being on the ballot, but a small number had a status of "Void," "Withdrew," or "Under Review." The candidates in these categories need to be ignored, while still being included in JSON exports in case anyone wants to see information about them.


*Note: This code is currently undergoing reorganization, and more extensive comments are being added. Additionally, the source data files needed to run this program will be added here once they have confidential information removed from them.*