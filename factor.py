import numpy as np


class DiscreteFactor:
    # noinspection PyNoneFunctionAssignment
    def __init__(self, variables, data=None, normalize=False, parameters=None):
        # variables = [(name, cardinality), (name, cardinality) ... ]
        # parameters = array (dtype=object) of same shape as data, containing parameter names

        # Short form: if only list of names, use cardinalities of 2
        try:
            dummy = variables[0].__iter__
            # use as is
        except AttributeError:
            # add default cardinality of 2
            variables = [(variable_name, 2) for variable_name in variables]

        self.variables = variables
        self.variable_set = set(variable[0] for variable in variables)
        self.cardinalities = dict(variables)
        self.variable_to_axis = dict((variable[0], i)
                                     for i, variable in enumerate(variables))
        self.axis_to_variable = dict((i, variable[0])
                                     for i, variable in enumerate(variables))
        self.parameters = parameters
        if data is not None:
            self.data = data
        else:
            self.data = np.ones(tuple(variable[1] for variable in variables))

        self.log_normalizer = np.log(1.0)
        if normalize:
            self.log_normalizer = np.log(self.data.sum())
            self.data /= np.exp(self.log_normalizer)
            self.log_normalizer = np.log(1.0)

    def marginalize(self, variable_names, normalize=False):
        # variable_names: variables to keep
        #print 'marg', self.data
        axes = [self.variable_to_axis[own_variable_name]
                for own_variable_name, own_variable_card in self.variables
                if own_variable_name not in variable_names]
        result_variables = [variable for variable in self.variables if variable[0] in variable_names]
        result_shape = [cardinality for name, cardinality in result_variables]

        if axes:
            result_data = np.apply_over_axes(np.sum, self.data, axes).reshape(result_shape)
            #print 'first'
            #print self, variable_names, normalize
            #print self.data
        else:  # Edge case where the original array is returned instead of a copy
            result_data = np.copy(self.data)
            #print 'second', variable_names, self

        result_log_norm = np.log(result_data.sum())
        #print 'susm', result_log_norm, result_data, self.data
        result_data = result_data / np.exp(result_log_norm)
        #print 'after exp div', result_data
        total_log_norm = self.log_normalizer + result_log_norm
        if normalize:
            total_log_norm = np.log(1.0)
        result_factor = DiscreteFactor(result_variables, result_data)
        result_factor.log_normalizer = total_log_norm

        return result_factor

    def multiply(self, other_factor, divide=False, update_inplace=True):
        #print 'mult start', self.data
        other_variable_order = [other_factor.axis_to_variable[other_axis]
                                for other_axis in xrange(len(other_factor.data.shape))]
        variables_in_self_not_in_other = [variable[0] for variable in self.variables
                                          if variable not in other_factor.variables]
        other_variable_order += variables_in_self_not_in_other
        #print 'other_var_ord', other_variable_order
        #print 'variables_in_self_not_ot', variables_in_self_not_in_other
        new_axis_order = [other_variable_order.index(self.axis_to_variable[axis])
                          for axis in xrange(len(other_variable_order))]

        new_shape = [card for card in other_factor.data.shape] + [1 for var in variables_in_self_not_in_other]
        reshaped_other_data = other_factor.data.reshape(new_shape)
        reordered_other_data = reshaped_other_data.transpose(new_axis_order)

        tile_shape = [self_card if self_card != other_card else 1
                      for self_card, other_card in zip(self.data.shape, reordered_other_data.shape)]

        tiled_other_data = np.tile(reordered_other_data, tile_shape)

        if not divide:
            result_data = self.data * tiled_other_data
            result_norm = self.log_normalizer + other_factor.log_normalizer
        else:
            result_data = self.data / tiled_other_data
            result_data = np.nan_to_num(result_data)
            #print 'if div', self.log_normalizer, other_factor.log_normalizer
            result_norm = self.log_normalizer - other_factor.log_normalizer
        if update_inplace:
            self.data = result_data
            self.log_normalizer = result_norm
        else:
            result_factor = DiscreteFactor(self.variables, result_data, parameters=self.parameters)
            result_factor.log_normalizer = result_norm
            #print 'result norm mult', result_norm, result_factor.data
            #print 'result norm mult', self.data
            #result_factor.data = result_data
            return result_factor

    def get_potential(self, variable_list):
        """
        Return the entry in the table for the assignment of variables.
        variable_list: list of pairs. Each pair is (variable_name, assignment)
        """
        array_position = [slice(self.cardinalities[self.axis_to_variable[axis]])
                          for axis in xrange(len(self.variables))]
        for var, assignment in variable_list:
            if var in self.cardinalities:
                array_position[self.variable_to_axis[var]] = assignment
        #print 'logn', self.log_normalizer
        #print 'da, ln', self.data[tuple(array_position)], np.exp(self.log_normalizer)
        return self.data[tuple(array_position)] * np.exp(self.log_normalizer)

    def set_evidence(self, evidence, normalize=False, inplace=False):
        """
        Pin the variables to certain values
        param evidence: list of (variable, value) pairs
        return: new factor if inplace is True, else this factor.
        """
        array_position = [slice(self.cardinalities[self.axis_to_variable[axis]])
                          for axis in xrange(len(self.variables))]
        for var, assignment in evidence.items():
            if var in self.cardinalities:
                array_position[self.variable_to_axis[var]] = assignment

        multiplier = np.zeros_like(self.data)
        multiplier[tuple(array_position)] = 1

        if inplace:
            return_factor = self
        else:
            return_factor = DiscreteFactor(self.variables, 'placeholder', parameters=self.parameters)
        return_data = self.data * multiplier * 1.0

        total_log_norm = self.log_normalizer #+ np.log(result_norm)
        if normalize:
            result_norm = return_data.sum()
            return_data /= result_norm
            total_log_norm = np.log(1.0)
        return_factor.data = return_data
        return_factor.log_normalizer = total_log_norm
        #print 'set_ev', self.variables, return_data
        return return_factor

    def _rotate_other(self, other_factor):
        other_variable_order = [other_factor.axis_to_variable[other_axis]
                                for other_axis in xrange(len(other_factor.data.shape))]
        new_axis_order = [other_variable_order.index(self.axis_to_variable[axis])
                          for axis in xrange(len(other_variable_order))]
        #print self.variables
        #print other_factor.variables
        #print other_variable_order
        #print new_axis_order
        return other_factor.data.transpose(new_axis_order)

    def get_data(self):
        """ Return factor potential. """
        return self.data * np.exp(self.log_normalizer)

    def __str__(self):
        return 'F{' + ', '.join(str(var) for var, card in self.variables) + '}'

    def __repr__(self):
        return self.__str__()
