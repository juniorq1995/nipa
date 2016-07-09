#!/usr/bin/env python
"""
This module contains functions that create dictionaries for
transforming integer months to appropriate strings for 
downloading data, opendapping to IRI, etc
"""

def int_to_month():
	"""
	This function is used by data_load.create_data_parameters
	"""
	i2m = {
	-8	: 'Apr',
	-7	: 'May',
	-6	: 'Jun',
	-5	: 'Jul',
	-4	: 'Aug',
	-3	: 'Sep',
	-2	: 'Oct',
	-1	: 'Nov',
	0	: 'Dec',
	1	: 'Jan',
	2	: 'Feb',
	3	: 'Mar',
	4	: 'Apr',
	5	: 'May',
	6	: 'Jun',
	7 	: 'Jul',
	8	: 'Aug',
	9	: 'Sept',
	10	: 'Oct',
	11	: 'Nov',
	12	: 'Dec',
	13	: 'Jan',
	14	: 'Feb',
	15	: 'Mar',
		}
	return i2m

def slp_tf():
	d = {
		-4	: '08',
		-3	: '09',
		-2	: '10',
		-1	: '11',
		0	: '12',
		1	: '01',
		2	: '02',
		3	: '03',
		4	: '04', 
		5	: '05',
		6 	: '06',
		7	: '07',
		8	: '08',
		9	: '09',
		10	: '10',
		11	: '11',
		12	: '12',
		13	: '01',
		14	: '02', 
		15	: '03',
		}
	return d