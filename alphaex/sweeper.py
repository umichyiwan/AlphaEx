#######################################################################
# Copyright (C) 2019 Yi Wan(wan6@ualberta.ca)                         #
# Permission given to modify the code as long as you keep this        #
# declaration at the top                                              #
#######################################################################


import json


class Sweeper(object):
    """
    The purpose of this class is to take an index, identify a configuration
    of variables and create a Config object
    Important: variables part of the sweep are provided in a list
    """
    def __init__(self, config_file):
        with open(config_file) as f:
            self.config_dict = json.load(f)
        self.total_combinations = 1
        self.set_num_combinations()

    def set_num_combinations(self):
        # calculating total_combinations
        self.set_num_combinations_helper(self.config_dict)
        self.total_combinations = self.config_dict['num_combinations']

    def set_num_combinations_helper(self, config_dict):
        num_combinations_in_list = 1
        for _, values in config_dict.items():
            num_combinations = 0
            for value in values:
                if type(value) is dict:
                    self.set_num_combinations_helper(value)
                    num_combinations += value['num_combinations']
                else:
                    num_combinations += 1
            num_combinations_in_list *= num_combinations
        config_dict['num_combinations'] = num_combinations_in_list
        return num_combinations_in_list

    def parse(self, idx):
        rtn_dict = dict()
        rtn_dict['run'] = int(idx / self.total_combinations)
        # rtn_dict['param_setting'] = idx % self.total_combinations
        
        self.parse_helper(idx, self.config_dict, rtn_dict)
        
        return rtn_dict
    
    def parse_helper(self, idx, config_dict, rtv_dict):
        cumulative = 1
        # Populating sweep variables
        for variable, values in config_dict.items():
            if variable == 'num_combinations':
                continue
            num_combinations = self.get_num_combinations(values)
            value, relative_idx = self.get_value_and_relative_idx(values, int(idx / cumulative) % num_combinations)
            if type(value) is dict:
                self.parse_helper(relative_idx, value, rtv_dict)
            else:
                rtv_dict[variable] = value
            cumulative *= num_combinations
    
    @ staticmethod
    def get_num_combinations(values):
        num_values = 0
        for value in values:
            if type(value) is dict:
                num_values += value['num_combinations']
            else:
                num_values += 1
        return num_values
    
    @ staticmethod
    def get_value_and_relative_idx(values, idx):
        num_values = 0
        for value in values:
            if type(value) is dict:
                temp = value['num_combinations']
            else:
                temp = 1
            if idx < num_values + temp:
                return value, idx - num_values
            num_values += temp
        return num_values

    def search(self, search_dict, num_runs):
        """
            For any key in self.config_dict, if search_dict also has the key, use the corresponding value.
            Otherwise enumerate all values that key could take according to self.config_dict file.
            In addition, for each variable combination, list id corresponding to each run.
            For example, suppose self.total_combinations = 10 and we want to list ids corresponding to 4 runs, then
            the 5th variable combination corresponds to a 4-element list of ids [5, 15, 25, 35].
            :param
                cfg: choose parameter settings according to cfg. Parameters in cfg can only take one value.
                num_runs: number of runs
            :return: a list of combinations of variables.
		"""
        
        param_setting_list = []
    
        for idx in range(self.total_combinations):
    
            temp_dict = self.parse(idx)
            
            valid_temp_dict = True
            for key, value in search_dict.items():
                if key not in temp_dict:
                    valid_temp_dict = False
                    break
            
            if valid_temp_dict is False:
                continue

            param_setting_list.append({'ids': [idx + run * self.total_combinations for run in range(num_runs)]})
                
            for key, value in temp_dict.items():
                if key in search_dict and search_dict[key] != value:
                    param_setting_list = param_setting_list[:-1]
                    break
                param_setting_list[-1][key] = value
    
        return param_setting_list
