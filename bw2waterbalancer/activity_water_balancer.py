from brightway2 import *
import warnings
from .utils import ParameterNameGenerator
from presamples.models.parameterized import ParameterizedBrightwayModel as PBM
from numpy import inf
import copy

class ActivityWaterBalancer():
    """Balances water exchange samples at the activity level

    Upon instantiation, will identify and classify all water exchanges.
    New generic parameter names are also generated for each water exchange.
    Use Method `generate_samples` to actually generate samples. This is usually
    invoked via a DatabaseWaterBalancer instance.

    Parameters:
    ------------
       act_key: tuple
           Key of the activity.
       database_water_balancer: DatabaseWaterBalancer
           Instance of a DatabaseWaterBalancer
    """
    def __init__(self, act_key, database_water_balancer):
        self.act = get_activity(act_key)
        for keys in [
            'techno_transfo_keys', 'techno_treat_keys',
            'bio_ress_keys', 'bio_emission_keys',
            'all_water_keys', 'group'
        ]:
            setattr(self, keys, getattr(database_water_balancer, keys))
        water_exchanges = [
            exc for exc in self.act.exchanges()
            if exc.input.key in self.all_water_keys
        ]
        if not water_exchanges:
            self.strategy = "skip"
            self.water_exchanges = water_exchanges
        else:
            self._move_exchange_formulas_to_temp()
            self.water_exchanges = [
                exc for exc in self.act.exchanges()
                if exc.input.key in self.all_water_keys
            ]
            self.water_exchange_input_keys = [exc.input.key for exc in self.water_exchanges]
            self.water_exchange_types = [self._get_type(exc) for exc in self.water_exchanges]
            namer = ParameterNameGenerator()
            self.water_exchange_param_names = [namer['water_param'] for _ in range(len(self.water_exchanges))]
            self.activity_params = []

    def generate_samples(self, iterations=1000):
        """Calls other methods in order and adds parameters to group

        Parameters:
        ------------
           iterations: int
               Number of iterations in sample.
        """
        if not self._processed():
            self.activity_params = []
            self._identify_strategy()
            self._define_balancing_parameters()
        if self.strategy == 'skip':
            return []
        self._move_water_formulas_to_exchange()
        self._move_activity_parameters_to_temp()
        parameters.new_activity_parameters(self.activity_params, self.group)
        parameters.add_exchanges_to_group(self.group, self.act)
        parameters.recalculate()
        pbm = PBM(self.group)
        pbm.load_parameter_data()
        pbm.calculate_stochastic(iterations, update_amounts=True)
        pbm.calculate_matrix_presamples()
        self.matrix_data = pbm.matrix_data
        parameters.remove_from_group(self.group, self.act)
        self.act['parameters'] = []
        self.act.save()
        self.activity_params = []
        self._restore_activity_parameters()
        self._restore_exchange_formulas()
        return self.matrix_data

    def _identify_strategy(self):
        """Identify appropriate strategy to use for activity"""

        if not self.water_exchanges:
            return 'skip'
        for i, exc in enumerate(self.water_exchanges):
            if self.water_exchange_types[i] == 'skip':
                continue
            exc['to_kg_conversion_factor'] = self._get_conversion_factor_to_kg(exc)
            if exc['to_kg_conversion_factor'] is None:
                self.water_exchange_types[i] = 'skip'
                continue  # Can't deal with this exchange, unit not understood
            exc['abnormal_sign'] = self._check_sign(exc, self.water_exchange_types[i])
            exc.save()
        out_exc_types = ['techno_transfo_output', 'techno_treat_input', 'bio_emission']
        in_exc_types = ['techno_transfo_input', 'techno_treat_output', 'bio_ress']

        all_exc_out = [
            exc for i, exc in enumerate(self.water_exchanges)
            if self.water_exchange_types[i] in out_exc_types
        ]
        all_exc_in = [
            exc for i, exc in enumerate(self.water_exchanges)
            if self.water_exchange_types[i] in in_exc_types
        ]

        # Identify non-zero exchanges
        non_zero_in = [exc for exc in all_exc_in if exc['amount'] != 0]
        non_zero_out = [exc for exc in all_exc_out if exc['amount'] != 0]

        # If there isn't at least one non-zero input water exchange and one non-zero
        # output water exchange, skip
        if any([not non_zero_in, not non_zero_out]):
            self.strategy = "skip"
            return

        # Identify water exchanges with uncertainty
        exc_with_uncertainty_inputs = [exc for exc in all_exc_in if exc.get('uncertainty type', 0) != 0]
        exc_with_uncertainty_outputs = [exc for exc in all_exc_out if exc.get('uncertainty type', 0) != 0]

        # If there aren't any uncertain water exchanges, skip
        if len(exc_with_uncertainty_inputs + exc_with_uncertainty_outputs) == 0:
            self.strategy = "skip"
        # If there is only one uncertain water exchange, set_static
        elif len(exc_with_uncertainty_inputs + exc_with_uncertainty_outputs) == 1:
            self.strategy = "set_static"
        # If there are no uncertain inputs, inverse strategy (i.e. rescale outputs)
        elif len(exc_with_uncertainty_inputs) == 0:
            self.strategy = "inverse"
        # Apply default strategy otherwise (i.e. rescale inputs)
        else:
            self.strategy = "default"

    def _define_balancing_parameters(self):
        """Invoke strategy-specific method for generating parameters for rebalancing"""

        if getattr(self, 'strategy', None) is None:
            self._identify_strategy()
        if self.strategy == 'skip':
            return
        if self.strategy == 'default':
            self._get_static_data_default()
        if self.strategy == 'inverse':
            self._get_static_data_inverse()
        if self.strategy == 'set_static':
            self._get_static_data_set_static()

    def _get_static_data_default(self):
        """Define activity-level and exchange-level parameters for default rebalancing

        Rebalancing based on rescaling variable inputs so that the ratio of
        inputs to outputs is equal to the same ratio in the static activity.
        """
        var_in_terms = []
        const_in_terms = []
        out_terms = []
        in_total = 0
        out_total = 0

        for i, exc in enumerate(self.water_exchanges):
            param_name = self.water_exchange_param_names[i]
            water_exchange_type = self.water_exchange_types[i]
            exc_amount_value = exc.get('amount', 0) * exc.get('to_kg_conversion_factor')
            exc_amount_string = "{} * {}".format(exc['to_kg_conversion_factor'], self.water_exchange_param_names[i])
            if water_exchange_type in ['techno_treat_output', 'techno_treat_input']:
                exc_amount_value *= -1
                exc_amount_string = "-" + exc_amount_string
            if water_exchange_type in ['techno_transfo_input', 'techno_treat_output', 'bio_ress']:
                # add amount to appropriate total for calculating ratio and balance
                in_total += exc_amount_value
                # generate term for ratio equation
                term = exc_amount_string
                # add exchange to activity parameters (exchange parameter will
                # simply hook to this parameter)
                self.activity_params.append(self._convert_exchange_to_param(exc, param_name))
                if exc.get('uncertainty type', 0) != 0:
                    # Add term to variable portion of inputs
                    var_in_terms.append(term)
                    # Add hook to exchange, with scaling
                    exc['water_formula'] = "{} * scaling".format(param_name)
                    exc.save()
                else:
                    # Add term to constant portion of inputs
                    const_in_terms.append(term)
                    # Add hook to exchange, without scaling (constant)
                    exc['water_formula'] = param_name
                    exc.save()
            elif water_exchange_type in ['techno_transfo_output', 'techno_treat_input', 'bio_emission']:
                out_total += exc_amount_value
                # generate term for ratio equation
                term = exc_amount_string
                out_terms.append(term)
                # Add hook to exchange
                exc['water_formula'] = param_name
                exc.save()
                # Add parameter to activity parameters
                self.activity_params.append(self._convert_exchange_to_param(exc, param_name))

        self.in_total = in_total
        self.out_total = out_total
        self.static_ratio = in_total / out_total if out_total!=0 else inf
        self.static_balance = in_total - out_total
        self.activity_params.append(
            {
                'name': 'static_ratio',
                'database': exc.output['database'],
                'code': exc.output['code'],
                'amount': self.static_ratio,
                'uncertainty type': 0,
                'loc': self.static_ratio,
            }
        )
        out_term = self._get_term(out_terms)
        const_in_term = self._get_term(const_in_terms, on_empty=0)
        var_in_term = self._get_term(var_in_terms)
        self.activity_params.append(
            {
                'name': 'scaling',
                'formula': "({}*{}-{})/({})".format(self.static_ratio, out_term, const_in_term, var_in_term),
                'database': exc.output['database'],
                'code': exc.output['code'],
            },
        )
        self.activity_params.append(
            {
                'name': 'ratio',
                'formula': "(scaling * {} + {})/{}".format(var_in_term, const_in_term, out_term),
                'database': exc.output['database'],
                'code': exc.output['code'],
            },
        )

    def _get_static_data_inverse(self):
        """Define activity-level and exchange-level parameters for inverse rebalancing

        Rebalancing based on rescaling variable outputs so that the ratio of
        outputs to inputs is equal to the same ratio in the static activity.
        """
        var_out_terms = []
        const_out_terms = []
        in_terms = []
        in_total = 0
        out_total = 0

        for i, exc in enumerate(self.water_exchanges):
            param_name = self.water_exchange_param_names[i]
            water_exchange_type = self.water_exchange_types[i]
            exc_amount_value = exc.get('amount', 0) * exc.get('to_kg_conversion_factor')
            exc_amount_string = "{} * {}".format(exc['to_kg_conversion_factor'], self.water_exchange_param_names[i])
            if water_exchange_type in ['techno_treat_output', 'techno_treat_input']:
                exc_amount_value *= -1
                exc_amount_string = "-" + exc_amount_string
            if water_exchange_type in ['techno_transfo_output', 'techno_treat_input', 'bio_emission']:
                # add amount to appropriate total for calculating ratio and balance
                out_total += exc_amount_value
                # generate term for ratio equation
                term = exc_amount_string
                # add exchange to activity parameters (exchange parameter will
                # simply hook to this parameter)
                self.activity_params.append(self._convert_exchange_to_param(exc, param_name))
                if exc.get('uncertainty type', 0) != 0:
                    # Add term to variable portion of inputs
                    var_out_terms.append(term)
                    # Add hook to exchange, with scaling
                    exc['water_formula'] = "{} * scaling".format(param_name)
                    exc.save()
                else:
                    # Add term to constant portion of inputs
                    const_out_terms.append(term)
                    # Add hook to exchange, without scaling (constant)
                    exc['water_formula'] = param_name
                    exc.save()
            elif water_exchange_type in ['techno_transfo_input', 'techno_treat_output', 'bio_ress']:
                in_total += exc_amount_value
                # generate term for ratio equation
                term = exc_amount_string
                in_terms.append(term)
                # Add hook to exchange
                exc['water_formula'] = param_name
                exc.save()
                # Add parameter to activity parameters
                self.activity_params.append(self._convert_exchange_to_param(exc, param_name))

        self.in_total = in_total
        self.out_total = out_total
        self.static_ratio = out_total / in_total
        self.static_balance = out_total - in_total
        self.activity_params.append(
            {
                'name': 'static_ratio',
                'database': exc.output['database'],
                'code': exc.output['code'],
                'amount': self.static_ratio,
                'uncertainty type': 0,
                'loc': self.static_ratio,
            }
        )
        in_term = self._get_term(in_terms)
        const_out_term = self._get_term(const_out_terms, 0)
        var_out_term = self._get_term(var_out_terms, min_terms=2)
        self.activity_params.append(
            {
                'name': 'scaling',
                'formula': "({}*{}-{})/{}".format(self.static_ratio, in_term, const_out_term, var_out_term),
                'database': exc.output['database'],
                'code': exc.output['code'],
            },
        )
        self.activity_params.append(
            {
                'name': 'ratio',
                'formula': "(scaling * {} + {})/{}".format(var_out_term, const_out_term, in_term),
                'database': exc.output['database'],
                'code': exc.output['code'],
            },
        )

    def _get_static_data_set_static(self):
        """Define activity-level and exchange-level parameter to replace variable data with static data array
        """
        excs = [
            exc for exc in self.act.exchanges()
            if exc.input.key in self.all_water_keys
               and exc.get('uncertainty type', 0) != 0
        ]
        if len(excs) != 1:
            raise ValueError("Should only have one variable water exchange for 'set_static' strategy")
        exc = excs[0]
        exc['water_formula'] = 'cst'
        exc.save()
        self.static_ratio = 'Not calculated'
        self.static_balance = 'Not calculated'
        self.activity_params.append(self._convert_exchange_to_param(exc, 'cst'))
        self.activity_params[0]['uncertainty type'] = 0
        self.activity_params[0]['loc'] = exc['amount']

    def _convert_exchange_to_param(self, exc, p_name):
        """ Convert exchange to formatted parameter dict"""
        param = {
            'name': p_name,
            'amount': exc.get('amount', 0),
            'uncertainty type': exc.get('uncertainty type', 0),
            'loc': exc.get('loc', exc.get('amount', 0)),
            'scale': exc.get('scale'),
            'negative': exc.get('negative', False),
            'database': self.act.get('database'),
            'code': self.act.get('code'),
        }
        if exc.get('minimum') is not None:
            param['minimum'] = exc.get('minimum')
        if exc.get('maximum') is not None:
            param['maximum'] = exc.get('maximum')
        return param

    def _get_term(self, terms, on_empty=None, min_terms=None):
        """Translate a set of string terms to a single term to use in a formula """

        if min_terms is not None and len(terms) < min_terms :
            raise ValueError(
                "Expected at least {} terms, got {}".format(
                    min_terms, len(terms)
                )
            )
        if len(terms) == 0 and on_empty is None:
            raise ValueError("At least one term is needed for this strategy")
        elif len(terms) == 0:
            return str(on_empty)
        elif len(terms) == 1:
            return "{}".format(terms[0])
        else:
            return "({})".format(" + ".join(terms))

    def _check_sign(self, exc, exc_type):
        """Return True if sign consistent with type of exchange"""
        expect_positive = [
            'techno_transfo_output', 'techno_transfo_input',
            'bio_ress', 'bio_emission'
        ]
        expect_negative = [
            'techno_treat_output', 'techno_treat_input',
            'bio_ress', 'bio_emission'
        ]
        if exc_type in expect_positive and exc.get('amount', 0) < 1:
            return True
        elif exc_type in expect_negative and exc.get('amount', 0) > 1:
            return True
        else:
            return False

    def _get_type(self, exc):
        """Return type of water exchange"""
        input_key = exc.input.key
        if input_key in self.techno_transfo_keys:
            if exc.get('type') == 'production':
                return 'techno_transfo_output'
            if exc.get('type') == 'technosphere':
                return 'techno_transfo_input'
        elif input_key in self.techno_treat_keys:
            if exc.get('type') == 'production':
                return 'techno_treat_output'
            if exc.get('type') == 'technosphere':
                return 'techno_treat_input'
        elif input_key in self.bio_ress_keys:
            return 'bio_ress'
        elif input_key in self.bio_emission_keys:
            return 'bio_emission'
        # If not returned anything yet, it was impossible to classify
        warnings.warn(
            "Exchange type not understood for exchange "
            "between {} and {} ({}), not considered in balance.".format(
                exc.input.key, exc.output.key, exc.get('type')
            ))
        return 'skip'

    def _get_conversion_factor_to_kg(self, exc):
        """Return a conversion factor to kg"""
        if exc.get('unit') == 'kilogram':
            return 1
        elif exc.get('unit') == 'cubic meter':
            return 1000
        else:
            warnings.warn("Unit for exchange between {} and {} "
                          "not recognized, skipping".format(
                exc.input.key, exc.output.key
            ))

    def _reset(self):
        """Reset attributes"""
        self.strategy = None
        self.static_ratio = None
        self.static_balance = None
        self.activity_params = []

    def _processed(self):
        """ Return True if strategy, ratio and parameters already identified"""
        if getattr(self, 'strategy', None) is None:
            return False
        if self.strategy == 'skip':
            return True
        if any([
            getattr(self, 'static_ratio', None) is None,
            getattr(self, 'static_balance', None) is None,
            not getattr(self, 'activity_params', None),
            ]):
            return False
        return True

    def _move_exchange_formulas_to_temp(self):
        """ Temporarily move existing formulas to avoid conflicts

        Existing formulas are moved from `formulas` to `temp_formulas` so they
        don't get picked up by `new_activity_parameters` later.
        In fact, ecoinvent formulas often referred to chemical formulas for
        biosphere exchanges.

        Formulas can be restored with the `_restore_exchange_formulas` method.
        """
        for exc in self.act.exchanges():
            if 'formula' in exc:
                '''print(self.act, exc['name'], exc['formula'])'''
                exc['temp_formula'] = exc['formula']
                del exc['formula']
                exc.save()

    def _move_water_formulas_to_exchange(self):
        """ Move water balance formulas to formulas field"""
        for exc in self.act.exchanges():
            if 'water_formula' in exc:
                exc['formula'] = exc['water_formula']
                exc.save()

    def _move_activity_parameters_to_temp(self):
        """ Temporarily move existing activity parameters to avoid conflicts

        Existing parameters are moved from `act.parameters` to `act.temp_formulas`
        so they don't get picked up by `new_activity_parameters` later.

        Parameters can be restored with the `_restore_activity_parameters` method.
        """
        self.act['parameters_temp'] = copy.copy(self.act.get('parameters'))
        self.act['parameters'] = []
        self.act.save()

    def _restore_activity_parameters(self):
        """ Restore activity parameters that were temporarily removed

        Should be done once done working with the activity.
        """
        self.act['parameters'] = self.act.get('parameters_temp')
        del self.act['parameters_temp']
        self.act.save()

    def _restore_exchange_formulas(self):
        """ Restore exchange formulas that were temporarily removed

        Also moves formulas used for water balancing to 'water_formulas'
        Should be done once done working with the activity.
        """
        for exc in self.act.exchanges():
            if 'formula' in exc:
                exc['water_formula'] = copy.copy(exc.get('formula', None))
                del exc['formula']
            if 'temp_formula' in exc:
                exc['formula'] = exc.get('temp_formula', None)
                del exc['temp_formula']
            exc.save()

