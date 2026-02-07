# cub-scout-advancement-reporting
A script to help Den Leaders and Cubmasters track which requirements their scouts still need to complete to make rank. Also creates report cards for dens!

A note:
  This started as a quick and dirty project. Half of it is vibe coded, and I haven't put a ton of effort at the moment into making it the most efficient or the most beautiful code. This is really a quick and dirty MVP, but it works and I thought I'd share with the community so you can all help improve/make it better!

This script should be run in a folder and creates several different documents which are helpful for your Den Leaders and Cubmaster to manage advancement for your Pack!
1. Pack Report - contains an overview of scouts at all ranks and the percent complete towards their rank. Written to the directory where you run the script from.
2. Den Reports - Contains an overview of all the scouts in a den, a sorted list of remaining requirements to be completed (sorted by the requirements needed by the most scouts, and listing which scouts still need that requirement), and containing "report cards" that spell out which requirements each scout still needs. Copies are written to the directory where you run the script from, and to the rank-specific folder
3. Individual report cards - each rank will have a folder created for it, and in there will be written a "report card" file for each scout, outlining the requirements they still need to complete to make rank. Useful for emailing to parents as we get closer to the end of the scouting year!

**In order to run the script,**
1. You will need to generate a report from Internet Advancement (see below)
2. Put the csv report into the same directory as the script. Make sure it's titled "reportbuilder.csv"
3. run the script from the command line. (_python AdvancementReports.py_)

**In order to generate the report from Internet Advancement**
In Internet Advancement:
	Go to Reports on the side bar
	Click "New Report" and select "New Custom Report (Report Builder)"
	Check the following boxes:
		Show Empty Requirements
		Show Requirement Descriptions
		Show CS Adventure Requirements (Version: Latest)
		Show Current Rank
		Show Next Rank
	  All Scouts (deselect any who may have dropped/you don't want included)
		For each rank:
			Rank Status
			Rank Requirements
			Required Adventures
	click "Run"
	Click the CSV button to download the file
	Copy the csv into the AdvancementReports folder.
	Rename the file to "reportbuilder.csv"
	
	
