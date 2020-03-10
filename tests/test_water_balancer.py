import pytest
import numpy as np
from bw2waterbalancer.database_water_balancer import DatabaseWaterBalancer
from bw2waterbalancer.activity_water_balancer import ActivityWaterBalancer
from brightway2 import get_activity

def helper_get_matrix_data_sums_for_test(ab, matrix_data):
    """Helper function to return inputs and outputs in `matrix_data`

    Used in tests to check `matrix_data` 
    """
    samples_to_concat = []
    md_indices_inputs = []
    for md in matrix_data:
        md_indices_inputs.extend([i[0] for i in md[1]])
        samples_to_concat.append(md[0])
    indices_order = [md_indices_inputs.index(exc) for exc in ab.water_exchange_input_keys]
    samples = np.concatenate(samples_to_concat, axis=0)[indices_order]

    conversion_factor = np.array(
        [ab._get_conversion_factor_to_kg(exc) for exc in ab.water_exchanges]
    )
    in_exc = np.array(
        ['techno_transfo_input', 'techno_treat_output', 'bio_ress']
    )
    out_exc = np.array(
        ['techno_transfo_output', 'techno_treat_input', 'bio_emission']
    )
    out_filter = np.array(
        [1 if ab.water_exchange_types[i] in out_exc else 0 for i, exc in enumerate(ab.water_exchanges)]
    )
    in_filter = np.array(
        [1 if ab.water_exchange_types[i] in in_exc else 0 for i, exc in enumerate(ab.water_exchanges)]
    )
    waste_filter = np.array(
        [-1 if ab.water_exchange_types[i] in ['techno_treat_output', 'techno_treat_input'] else 1
         for i, exc in enumerate(ab.water_exchanges)]
    )
    in_totals = np.sum(
        ((in_filter * waste_filter * conversion_factor).reshape(-1, 1) * samples), axis=0
    )
    out_totals = np.sum(
        ((out_filter * waste_filter * conversion_factor).reshape(-1, 1) * samples), axis=0
    )
    return in_totals, out_totals


def test_no_such_database(data_for_testing):
    """Ensure error raised when db doesn't exist"""
    with pytest.raises(ValueError, match="Database no such db not imported"):
        wb = DatabaseWaterBalancer(ecoinvent_version=None, database_name="no such db")


def test_no_such_biosphere(data_for_testing):
    """Ensure error raised when biosphere db doesn't exist"""
    with pytest.raises(ValueError, match="Database no such biosphere not imported"):
        wb = DatabaseWaterBalancer(ecoinvent_version=None, database_name="test_db", biosphere="no such biosphere")


def test_no_such_database_version(data_for_testing):
    """Ensure warning raised when ecoinvent version doesn't exist"""
    with pytest.warns(UserWarning, match="No data available for version x, using version 3.6 "
                          "instead, which may result in some errors"):
        wb = DatabaseWaterBalancer(ecoinvent_version='x', database_name="test_db", biosphere="biosphere")
        assert wb.ecoinvent_version == '3.6'


def test_identify_exchanges(data_for_testing):
    """Find and classify all water elementary flows in biosphere"""

    wb = DatabaseWaterBalancer(ecoinvent_version='test_db', database_name="test_db", biosphere="biosphere")
    expected_bio_ress_keys = [
        ('biosphere', 'Water 1, from nature, in kg'),
        ('biosphere', 'Water 2, from nature, in kg'),
        ('biosphere', 'Water, from nature, in m3'),
    ]
    expected_bio_emission_keys = [
        ('biosphere', 'Water 1, to water, in kg'),
        ('biosphere', 'Water 2, to water, in kg'),
        ('biosphere', 'Water, to water, in m3'),
        ('biosphere', 'Water, to air, in kg'),
        ('biosphere', 'Water, to air, in m3'),
    ]
    expected_techno_transfo_keys = [('test_db', code) for code in "STUV"]
    expected_techno_treat_keys = [('test_db', code) for code in "LMNOPQR"]

    expected_all_keys = expected_bio_emission_keys \
                        + expected_bio_ress_keys \
                        + expected_techno_transfo_keys \
                        + expected_techno_treat_keys

    assert set(wb.bio_ress_keys) == set(expected_bio_ress_keys)
    assert len(wb.bio_ress_keys) == len(expected_bio_ress_keys)
    assert set(wb.bio_emission_keys) == set(expected_bio_emission_keys)
    assert len(wb.bio_emission_keys) == len(expected_bio_emission_keys)
    assert set(wb.techno_transfo_keys) == set(expected_techno_transfo_keys)
    assert len(wb.techno_transfo_keys) == len(expected_techno_transfo_keys)
    assert set(wb.techno_treat_keys) == set(expected_techno_treat_keys)
    assert len(wb.techno_treat_keys) == len(expected_techno_treat_keys)
    assert set(wb.all_water_keys) == set(expected_all_keys)
    assert len(wb.all_water_keys) == len(expected_all_keys)


def test_water_exchange_formulas_removed(data_for_testing):
    """ Make sure formulas are properly removed from exchanges"""
    act = get_activity(("test_db", "A"))
    exc = [exc for exc in act.exchanges() if exc.input.key==('biosphere', 'Water 1, from nature, in kg')][0]
    assert exc['formula'] == 'some_good_formula'
    wb = DatabaseWaterBalancer(ecoinvent_version='test_db', database_name="test_db", biosphere="biosphere")
    ab = ActivityWaterBalancer(('test_db', 'A'), wb)
    exc_1 = [exc for exc in ab.act.exchanges() if exc.input.key == ('biosphere', 'Water 1, from nature, in kg')][0]
    exc_in_list_1 = [exc for exc in ab.water_exchanges if exc.input.key == ('biosphere', 'Water 1, from nature, in kg')][
        0]
    exc_2 = [exc for exc in ab.act.exchanges() if exc.input.key == ('biosphere', 'Water 2, from nature, in kg')][0]
    exc_in_list_2 = [exc for exc in ab.water_exchanges if exc.input.key == ('biosphere', 'Water 2, from nature, in kg')][
        0]

    assert exc_1.get('formula') is None
    assert exc_in_list_1.get('formula') is None
    assert exc_1.get('temp_formula') == 'some_good_formula'
    assert exc_in_list_1.get('temp_formula') == 'some_good_formula'
    assert exc_2.get('formula') is None
    assert exc_in_list_2.get('formula') is None
    assert exc_2.get('temp_formula') == 'some bad formula'
    assert exc_in_list_2.get('temp_formula') == 'some bad formula'

    ab._define_balancing_parameters()

    exc_1 = [exc for exc in ab.act.exchanges() if exc.input.key == ('biosphere', 'Water 1, from nature, in kg')][0]
    exc_in_list_1 = [exc for exc in ab.water_exchanges if exc.input.key == ('biosphere', 'Water 1, from nature, in kg')][
        0]
    exc_2 = [exc for exc in ab.act.exchanges() if exc.input.key == ('biosphere', 'Water 2, from nature, in kg')][0]
    exc_in_list_2 = [exc for exc in ab.water_exchanges if exc.input.key == ('biosphere', 'Water 2, from nature, in kg')][
        0]

    assert exc_1.get('formula') is None
    assert exc_1.get('temp_formula') == 'some_good_formula'
    assert exc_1.get('water_formula') is not None
    assert exc_in_list_1.get('formula') is None
    assert exc_in_list_1.get('temp_formula') == 'some_good_formula'
    assert exc_in_list_1.get('water_formula') is not None

    assert exc_2.get('formula') is None
    assert exc_2.get('temp_formula') == 'some bad formula'
    assert exc_2.get('water_formula') is not None
    assert exc_in_list_2.get('formula') is None
    assert exc_in_list_2.get('temp_formula') == 'some bad formula'
    assert exc_in_list_2.get('water_formula') is not None

    ab.generate_samples(2)
    exc_1 = [exc for exc in ab.act.exchanges() if exc.input.key == ('biosphere', 'Water 1, from nature, in kg')][0]
    exc_2 = [exc for exc in ab.act.exchanges() if exc.input.key == ('biosphere', 'Water 2, from nature, in kg')][0]
    assert exc_1.get('formula') == 'some_good_formula'
    assert exc_1.get('temp_formula') is None
    assert exc_2.get('formula') == 'some bad formula'
    assert exc_2.get('temp_formula') is None


def test_initially_unprocessed(data_for_testing):
    """Ensure processind happens at right moment """
    wb = DatabaseWaterBalancer(ecoinvent_version='test_db', database_name="test_db", biosphere="biosphere")
    ab = ActivityWaterBalancer(('test_db', 'A'), wb)
    assert not ab._processed()
    ab._identify_strategy()
    assert not ab._processed()
    ab._define_balancing_parameters()
    assert ab._processed()


def test_reset(data_for_testing):
    """Check _reset function"""
    wb = DatabaseWaterBalancer(ecoinvent_version='test_db', database_name="test_db", biosphere="biosphere")
    ab = ActivityWaterBalancer(('test_db', 'A'), wb)
    ab._identify_strategy()
    ab._define_balancing_parameters()
    assert ab._processed()
    ab._reset()
    assert not ab._processed()
    assert getattr(ab, "static_ratio") is None
    assert getattr(ab, "static_balance") is None
    assert getattr(ab, "activity_params") == []


def test_rebalance_default_ratio_1(data_for_testing):
    wb = DatabaseWaterBalancer(ecoinvent_version='test_db', database_name="test_db", biosphere="biosphere")
    assert wb.matrix_indices == []
    assert wb.matrix_samples is None
    ab = ActivityWaterBalancer(('test_db', 'A'), wb)
    ab._identify_strategy()
    assert ab.strategy == 'default'
    ab._define_balancing_parameters()
    assert ab.static_ratio == 1
    assert ab.static_balance == 0
    matrix_data = ab.generate_samples(5)
    assert matrix_data[0][0].shape[1] == 5
    assert matrix_data[0][0].shape[0] == 5
    assert matrix_data[1][0].shape[1] == 5
    assert matrix_data[1][0].shape[0] == 4
    in_sum, out_sum = helper_get_matrix_data_sums_for_test(ab, matrix_data)
    assert np.allclose(in_sum/out_sum, ab.static_ratio)
    wb.add_samples_for_act(ab.act, 5)
    assert len(wb.matrix_indices)==len(ab.water_exchanges)
    assert wb.matrix_samples.shape[0] == len(ab.water_exchanges)
    assert wb.matrix_samples.shape[1] == 5


def test_rebalance_inverse_ratio_1(data_for_testing):
    wb = DatabaseWaterBalancer(ecoinvent_version='test_db', database_name="test_db", biosphere="biosphere")
    ab = ActivityWaterBalancer(('test_db', 'B'), wb)
    ab._identify_strategy()
    assert ab.strategy == 'inverse'
    ab._define_balancing_parameters()
    assert ab.static_ratio == 1
    assert ab.static_balance == 0
    matrix_data = ab.generate_samples(5)
    assert matrix_data[0][0].shape[1] == 5
    assert matrix_data[0][0].shape[0] == 5
    assert matrix_data[1][0].shape[1] == 5
    assert matrix_data[1][0].shape[0] == 4
    in_sum, out_sum = helper_get_matrix_data_sums_for_test(ab, matrix_data)
    assert np.allclose(out_sum/in_sum, ab.static_ratio)


def test_rebalance_default_ratio_2(data_for_testing):
    wb = DatabaseWaterBalancer(ecoinvent_version='test_db', database_name="test_db", biosphere="biosphere")
    ab = ActivityWaterBalancer(('test_db', 'C'), wb)
    ab._identify_strategy()
    assert ab.strategy == 'default'
    ab._define_balancing_parameters()
    assert ab.static_ratio == 2
    assert ab.static_balance == 20
    matrix_data = ab.generate_samples(5)
    assert matrix_data[0][0].shape[1] == 5
    assert matrix_data[0][0].shape[0] == 5
    assert matrix_data[1][0].shape[1] == 5
    assert matrix_data[1][0].shape[0] == 4
    in_sum, out_sum = helper_get_matrix_data_sums_for_test(ab, matrix_data)
    assert np.allclose(in_sum/out_sum, ab.static_ratio)


def test_rebalance_inverse_ratio_2(data_for_testing):
    wb = DatabaseWaterBalancer(ecoinvent_version='test_db', database_name="test_db", biosphere="biosphere")
    ab = ActivityWaterBalancer(('test_db', 'D'), wb)
    ab._identify_strategy()
    assert ab.strategy == 'inverse'
    ab._define_balancing_parameters()
    assert ab.static_ratio == 0.5
    assert ab.static_balance == -20
    matrix_data = ab.generate_samples(5)
    assert matrix_data[0][0].shape[1]==5
    assert matrix_data[1][0].shape[1] == 5
    in_sum, out_sum = helper_get_matrix_data_sums_for_test(ab, matrix_data)
    assert np.allclose(out_sum/in_sum, ab.static_ratio)


def test_rebalance_default_ratio_1_mixed_units(data_for_testing):
    wb = DatabaseWaterBalancer(ecoinvent_version='test_db', database_name="test_db", biosphere="biosphere")
    ab = ActivityWaterBalancer(('test_db', 'E'), wb)
    ab._identify_strategy()
    assert ab.strategy == 'default'
    ab._define_balancing_parameters()
    assert ab.static_ratio == 1
    assert ab.static_balance == 0
    matrix_data = ab.generate_samples(5)
    assert matrix_data[0][0].shape[1] == 5
    assert matrix_data[0][0].shape[0] == 4
    assert matrix_data[1][0].shape[1] == 5
    assert matrix_data[1][0].shape[0] == 4
    in_sum, out_sum = helper_get_matrix_data_sums_for_test(ab, matrix_data)
    assert np.allclose(in_sum/out_sum, ab.static_ratio)


def test_rebalance_inverse_ratio_1_mixed_units(data_for_testing):
    wb = DatabaseWaterBalancer(ecoinvent_version='test_db', database_name="test_db", biosphere="biosphere")
    ab = ActivityWaterBalancer(('test_db', 'F'), wb)
    ab._identify_strategy()
    assert ab.strategy == 'inverse'
    ab._define_balancing_parameters()
    assert ab.static_ratio == 1
    assert ab.static_balance == 0
    matrix_data = ab.generate_samples(5)
    assert matrix_data[0][0].shape[1] == 5
    assert matrix_data[0][0].shape[0] == 4
    assert matrix_data[1][0].shape[1] == 5
    assert matrix_data[1][0].shape[0] == 4
    in_sum, out_sum = helper_get_matrix_data_sums_for_test(ab, matrix_data)
    assert np.allclose(out_sum/in_sum, ab.static_ratio)


def test_rebalance_set_static_one_input(data_for_testing):
    wb = DatabaseWaterBalancer(ecoinvent_version='test_db', database_name="test_db", biosphere="biosphere")
    ab = ActivityWaterBalancer(('test_db', 'G'), wb)
    ab._identify_strategy()
    assert ab.strategy == 'set_static'
    exc_initial = [
        exc for exc in ab.act.exchanges()
        if exc.input.key == ('biosphere', 'Water 1, from nature, in kg')
    ][0]
    assert exc_initial.get('uncertainty type', 0) == 2
    assert exc_initial.get('loc', 0) == np.log(exc_initial['amount'])

    ab._define_balancing_parameters()
    assert getattr(ab, "static_ratio") == "Not calculated"
    assert getattr(ab, "static_balance") == "Not calculated"
    exc_after = [
        exc for exc in ab.act.exchanges()
        if exc.input.key == ('biosphere', 'Water 1, from nature, in kg')
    ][0]
    assert exc_after.get('water_formula', 0) == 'cst'
    assert ab.activity_params[0]['name'] == 'cst'
    assert ab.activity_params[0]['amount'] == exc_initial['amount']
    assert ab.activity_params[0]['loc'] == exc_initial['amount']
    assert ab.activity_params[0]['uncertainty type'] == 0
    matrix_data = ab.generate_samples(5)
    assert len(matrix_data)==1
    assert matrix_data[0][0].shape[1]==5
    assert matrix_data[0][0].shape[0]==1
    assert np.allclose(np.ones(shape=(1, 5)), matrix_data[0][0])
    assert len(matrix_data[0][1]) == 1
    assert matrix_data[0][1][0] == (('biosphere', 'Water 1, from nature, in kg'), ('test_db', 'G'))


def test_rebalance_set_static_one_output(data_for_testing):
    wb = DatabaseWaterBalancer(ecoinvent_version='test_db', database_name="test_db", biosphere="biosphere")
    ab = ActivityWaterBalancer(('test_db', 'H'), wb)
    ab._identify_strategy()
    assert ab.strategy == 'set_static'
    exc_initial = [
        exc for exc in ab.act.exchanges()
        if exc.input.key == ('biosphere', 'Water 1, to water, in kg')
    ][0]
    assert exc_initial.get('uncertainty type', 0) == 2
    assert exc_initial.get('loc', 0) == np.log(exc_initial['amount'])

    ab._define_balancing_parameters()
    assert getattr(ab, "static_ratio", "Nope") == "Not calculated"
    assert getattr(ab, "static_balance", "Nope") == "Not calculated"
    exc_after = [
        exc for exc in ab.act.exchanges()
        if exc.input.key == ('biosphere', 'Water 1, to water, in kg')
    ][0]
    assert exc_after.get('water_formula', 0) == 'cst'
    assert ab.activity_params[0]['name'] == 'cst'
    assert ab.activity_params[0]['amount'] == exc_initial['amount']
    assert ab.activity_params[0]['loc'] == exc_initial['amount']
    assert ab.activity_params[0]['uncertainty type'] == 0
    matrix_data = ab.generate_samples(5)
    assert len(matrix_data) == 1
    assert matrix_data[0][0].shape[1] == 5
    assert matrix_data[0][0].shape[0] == 1
    assert np.allclose(np.ones(shape=(1, 5)), matrix_data[0][0])
    assert len(matrix_data[0][1]) == 1
    assert matrix_data[0][1][0] == (('biosphere', 'Water 1, to water, in kg'), ('test_db', 'H'))


def test_rebalance_skip_no_input(data_for_testing):
    wb = DatabaseWaterBalancer(ecoinvent_version='test_db', database_name="test_db", biosphere="biosphere")
    ab = ActivityWaterBalancer(('test_db', 'I'), wb)
    ab._identify_strategy()
    assert ab.strategy == 'skip'
    assert ab._processed()
    assert getattr(ab, "static_ratio", "Nope") is "Nope"
    assert getattr(ab, "static_balance", "Nope") is "Nope"
    assert ab.generate_samples() == []


def test_rebalance_skip_no_output(data_for_testing):
    wb = DatabaseWaterBalancer(ecoinvent_version='test_db', database_name="test_db", biosphere="biosphere")
    ab = ActivityWaterBalancer(('test_db', 'J'), wb)
    ab._identify_strategy()
    assert ab.strategy == 'skip'
    assert getattr(ab, "static_ratio", "Nope") is "Nope"
    assert getattr(ab, "static_balance", "Nope") is "Nope"


def test_rebalance_skip_no_uncertainty(data_for_testing):
    wb = DatabaseWaterBalancer(ecoinvent_version='test_db', database_name="test_db", biosphere="biosphere")
    ab = ActivityWaterBalancer(('test_db', 'K'), wb)
    ab._identify_strategy()
    assert ab.strategy == 'skip'
    assert getattr(ab, "static_ratio", "Nope") is "Nope"
    assert getattr(ab, "static_balance", "Nope") is "Nope"


def test_rebalance_default_ratio_1_ww(data_for_testing):
    wb = DatabaseWaterBalancer(ecoinvent_version='test_db', database_name="test_db", biosphere="biosphere")
    ab = ActivityWaterBalancer(('test_db', 'L'), wb)
    ab._identify_strategy()
    assert ab.strategy == 'default'
    ab._define_balancing_parameters()
    assert ab.static_ratio == 1
    assert ab.static_balance == 0
    matrix_data = ab.generate_samples(5)
    assert matrix_data[0][0].shape[1] == 5
    assert matrix_data[0][0].shape[0] == 2
    assert matrix_data[1][0].shape[1] == 5
    assert matrix_data[1][0].shape[0] == 2
    in_sum, out_sum = helper_get_matrix_data_sums_for_test(ab, matrix_data)
    assert np.allclose(in_sum/out_sum, ab.static_ratio)


def test_rebalance_default_ratio_1_ww_m3(data_for_testing):
    wb = DatabaseWaterBalancer(ecoinvent_version='test_db', database_name="test_db", biosphere="biosphere")
    ab = ActivityWaterBalancer(('test_db', 'M'), wb)
    ab._identify_strategy()
    assert ab.strategy == 'default'
    ab._define_balancing_parameters()
    assert ab.static_ratio == 1
    assert ab.static_balance == 0
    matrix_data = ab.generate_samples(5)
    assert matrix_data[0][0].shape[1] == 5
    assert matrix_data[0][0].shape[0] == 2
    assert matrix_data[1][0].shape[1] == 5
    assert matrix_data[1][0].shape[0] == 2
    in_sum, out_sum = helper_get_matrix_data_sums_for_test(ab, matrix_data)
    assert np.allclose(in_sum/out_sum, ab.static_ratio)


def test_rebalance_default_ratio_1_ww_inverse(data_for_testing):
    wb = DatabaseWaterBalancer(ecoinvent_version='test_db', database_name="test_db", biosphere="biosphere")
    ab = ActivityWaterBalancer(('test_db', 'N'), wb)
    ab._identify_strategy()
    assert ab.strategy == 'inverse'
    ab._define_balancing_parameters()
    assert ab.static_ratio == 1
    assert ab.static_balance == 0
    matrix_data = ab.generate_samples(5)
    assert matrix_data[0][0].shape[1] == 5
    assert matrix_data[0][0].shape[0] == 2
    assert matrix_data[1][0].shape[1] == 5
    assert matrix_data[1][0].shape[0] == 2
    in_sum, out_sum = helper_get_matrix_data_sums_for_test(ab, matrix_data)
    assert np.allclose(out_sum/in_sum, ab.static_ratio)


def test_rebalance_default_ratio_1_ww_inverse_m3(data_for_testing):
    wb = DatabaseWaterBalancer(ecoinvent_version='test_db', database_name="test_db", biosphere="biosphere")
    ab = ActivityWaterBalancer(('test_db', 'O'), wb)
    ab._identify_strategy()
    assert ab.strategy == 'inverse'
    ab._define_balancing_parameters()
    assert ab.static_ratio == 1
    assert ab.static_balance == 0
    matrix_data = ab.generate_samples(5)
    assert matrix_data[0][0].shape[1] == 5
    assert matrix_data[0][0].shape[0] == 2
    assert matrix_data[1][0].shape[1] == 5
    assert matrix_data[1][0].shape[0] == 2
    in_sum, out_sum = helper_get_matrix_data_sums_for_test(ab, matrix_data)
    assert np.allclose(out_sum/in_sum, ab.static_ratio)


def test_rebalance_default_ww_ratio_not_1(data_for_testing):
    wb = DatabaseWaterBalancer(ecoinvent_version='test_db', database_name="test_db", biosphere="biosphere")
    ab = ActivityWaterBalancer(('test_db', 'P'), wb)
    ab._identify_strategy()
    assert ab.strategy == 'default'
    ab._define_balancing_parameters()
    assert ab.static_ratio == 2
    assert ab.static_balance == 1
    matrix_data = ab.generate_samples(5)
    assert matrix_data[0][0].shape[1] == 5
    assert matrix_data[0][0].shape[0] == 2
    assert matrix_data[1][0].shape[1] == 5
    assert matrix_data[1][0].shape[0] == 2
    in_sum, out_sum = helper_get_matrix_data_sums_for_test(ab, matrix_data)
    assert np.allclose(in_sum/out_sum, ab.static_ratio)


def test_rebalance_inverse_ww_ratio_not_1(data_for_testing):
    wb = DatabaseWaterBalancer(ecoinvent_version='test_db', database_name="test_db", biosphere="biosphere")
    ab = ActivityWaterBalancer(('test_db', 'Q'), wb)
    ab._identify_strategy()
    assert ab.strategy == 'inverse'
    ab._define_balancing_parameters()
    assert ab.static_ratio == 0.5
    assert ab.static_balance == -1
    matrix_data = ab.generate_samples(5)
    assert matrix_data[0][0].shape[1] == 5
    assert matrix_data[0][0].shape[0] == 2
    assert matrix_data[1][0].shape[1] == 5
    assert matrix_data[1][0].shape[0] == 2
    in_sum, out_sum = helper_get_matrix_data_sums_for_test(ab, matrix_data)
    assert np.allclose(out_sum/in_sum, ab.static_ratio)


def test_rebalance_ww_market(data_for_testing):
    wb = DatabaseWaterBalancer(ecoinvent_version='test_db', database_name="test_db", biosphere="biosphere")
    ab = ActivityWaterBalancer(('test_db', 'R'), wb)
    ab._identify_strategy()
    assert ab.strategy == 'default'
    ab._define_balancing_parameters()
    assert ab.static_ratio == 1
    assert ab.static_balance == 0
    matrix_data = ab.generate_samples(5)
    assert matrix_data[0][0].shape[1] == 5
    assert matrix_data[0][0].shape[0] == 1
    assert matrix_data[1][0].shape[1] == 5
    assert matrix_data[1][0].shape[0] == 6
    in_sum, out_sum = helper_get_matrix_data_sums_for_test(ab, matrix_data)
    assert np.allclose(in_sum/out_sum, ab.static_ratio)


def test_rebalance_tap_water_default(data_for_testing):
    wb = DatabaseWaterBalancer(ecoinvent_version='test_db', database_name="test_db", biosphere="biosphere")
    ab = ActivityWaterBalancer(('test_db', 'S'), wb)
    ab._identify_strategy()
    assert ab.strategy == 'default'
    ab._define_balancing_parameters()
    assert ab.static_ratio == 1
    assert ab.static_balance == 0
    matrix_data = ab.generate_samples(5)
    assert matrix_data[0][0].shape[1] == 5
    assert matrix_data[0][0].shape[0] == 3
    assert matrix_data[1][0].shape[1] == 5
    assert matrix_data[1][0].shape[0] == 1
    in_sum, out_sum = helper_get_matrix_data_sums_for_test(ab, matrix_data)
    assert np.allclose(in_sum/out_sum, ab.static_ratio)


def test_rebalance_tap_water_default_m3(data_for_testing):
    wb = DatabaseWaterBalancer(ecoinvent_version='test_db', database_name="test_db", biosphere="biosphere")
    ab = ActivityWaterBalancer(('test_db', 'T'), wb)
    ab._identify_strategy()
    assert ab.strategy == 'default'
    ab._define_balancing_parameters()
    assert ab.static_ratio == 1
    assert ab.static_balance == 0
    matrix_data = ab.generate_samples(5)
    assert matrix_data[0][0].shape[1] == 5
    assert matrix_data[0][0].shape[0] == 3
    assert matrix_data[1][0].shape[1] == 5
    assert matrix_data[1][0].shape[0] == 1
    in_sum, out_sum = helper_get_matrix_data_sums_for_test(ab, matrix_data)
    assert np.allclose(in_sum/out_sum, ab.static_ratio)


def test_rebalance_tap_water_market(data_for_testing):
    wb = DatabaseWaterBalancer(ecoinvent_version='test_db', database_name="test_db", biosphere="biosphere")
    ab = ActivityWaterBalancer(('test_db', 'U'), wb)
    ab._identify_strategy()
    assert ab.strategy == 'set_static'
    matrix_data = ab.generate_samples(5)
    assert len(matrix_data)==1
    assert matrix_data[0][0].shape[1]==5
    assert matrix_data[0][0].shape[0]==1
    assert np.allclose(0.1*np.ones(shape=(1, 5)), matrix_data[0][0])
    assert len(matrix_data[0][1]) == 1
    assert matrix_data[0][1][0] == (('biosphere', 'Water 1, to water, in kg'), ('test_db', 'U'))


def test_rebalance_tap_water_market_losses(data_for_testing):
    wb = DatabaseWaterBalancer(ecoinvent_version='test_db', database_name="test_db", biosphere="biosphere")
    ab = ActivityWaterBalancer(('test_db', 'V'), wb)
    ab._identify_strategy()
    assert ab.strategy == 'default'
    ab._define_balancing_parameters()
    assert ab.static_ratio == 1
    assert ab.static_balance == 0
    matrix_data = ab.generate_samples(5)
    assert matrix_data[0][0].shape[1]==5
    assert matrix_data[0][0].shape[0] == 1
    assert matrix_data[1][0].shape[1] == 5
    assert matrix_data[1][0].shape[0] == 3
    production_indices = [1 if t[2]=='production' else 0 for t in matrix_data[1][1]]
    techno_indices = [0 if t[2]=='production' else 1 for t in matrix_data[1][1]]
    in_total = (matrix_data[1][0]*np.array(techno_indices).reshape(-1,1)).sum(axis=0)
    out_total = (matrix_data[1][0] * np.array(production_indices).reshape(-1, 1)).sum(axis=0) + matrix_data[0][0]
    assert np.allclose(in_total, out_total)


def test_all_matrix_data_and_presamples(data_for_testing):
    wb = DatabaseWaterBalancer(ecoinvent_version='test_db', database_name="test_db", biosphere="biosphere")
    assert wb.matrix_indices==[]
    assert wb.matrix_samples is None
    wb.add_samples_for_all_acts(5)
    assert len(wb.matrix_indices)==98
    assert wb.matrix_samples.shape == (98, 5)
    id_, dirpath = wb.create_presamples(id_="test")
    indices_0 = np.load(dirpath/"{}.0.indices.npy".format(id_))
    indices_1 = np.load(dirpath / "{}.1.indices.npy".format(id_))
    samples_0 = np.load(dirpath/"{}.0.samples.npy".format(id_))
    samples_1 = np.load(dirpath / "{}.1.samples.npy".format(id_))
    assert indices_0.shape[0] + indices_1.shape[0] == 97
    assert samples_0.shape[1] == 5
    assert samples_1.shape[1] == 5
    assert samples_0.shape[0] + samples_1.shape[0] == 97
