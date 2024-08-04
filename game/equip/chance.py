import random

def lower_zero(num):
	count=1
	while True:
		if num*(10**count)<1:
			count+=1
			continue
		else:
			break
	num = num*(10**count)
	return count, num

def check(num):
	if num > round(num):
		num = round(num)+1
	return num
	
def get_random(num_to_list,zeros):
	chance_list =  []
	if zeros == 0:
		border = 100
	else:
		border = (10**zeros)
		
	while len(chance_list) < num_to_list:
	
		num = random.randint(0,border)
		if num in chance_list:
			num = random.randint(0,border)
		else:
			chance_list.append(num)
			
	check = random.randint(0,border)
	if check in chance_list:
		return True
	else:
		return False

def chance(percents):
	zeros = None
	num_to_list = None
	try:
		percents = percents.replace('%','')
	except:
		pass
		
	try:
		percents = int(percents)
	except ValueError:
		percents = float(percents)
	
	if type(percents)== float:
		if percents <1:
			zeros,num_to_list=lower_zero(percents)
			num_to_list = check(num_to_list)
		else:
			zeros = 0
			num_to_list = check(num_to_list)
		return get_random(num_to_list,zeros)
	else:
		return get_random(percents,0)