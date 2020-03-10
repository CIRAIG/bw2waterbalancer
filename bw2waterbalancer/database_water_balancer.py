from brightway2 import *
import numpy as np
from bw2data.backends.peewee.schema import ExchangeDataset
import json
import warnings
from pathlib import Path
import pyprind
from .activity_water_balancer import ActivityWaterBalancer
from presamples import create_presamples_package, split_inventory_presamples

class DatabaseWaterBalancer():
    """Generate database-level balanced water samples to override unbalanced samples

    Developed to bring some sanity to independently sampled water exchange
    values, specifically for the ecoinvent database. Because different water
    exchanges in this database are not parameterized (at least after datasets
    have gone through system modelling algorithms), the independently sampled
    water exchange values result in faulty water balances at an individual unit
    processes level. This database-level package and its associated activity-level
    package `ActivityWaterBalancer` rebalance water samples to ensure that the
    ratio of water in to water out is maintained across MonteCarlo iterations.
    The balanced samples can be stored in a `presamples` package,
    see https://presamples.readthedocs.io/

    This package has database-level attributes and methods. It identifies and
    classifies water exchanges in a database. Actual sample generation
    is carried out in activity-level class `ActivityWaterBalancer`, called here
    from method `add_samples_for_act`.

    Parameters:
    -----------
    ecoinvent_version: string
        ecoinvent release number. Used to identify correct list of water
        exchanges. If not supplied, or of supplied string does not match with
        a version that is covered by, code will default to the latest
        available version.
    database_name: string
        Name of the LCI database in the brightway2 project
    biosphere: string, default='biosphere3'
        Name of the biosphere database in the brighway2 database
    group: string, default='water'
        Name of the parameter group name. Used in the generation of samples.

    Attributes:
    -----------
    all_water_keys: list
        List of all keys of activities with reference exchanges that are
        water (wastewater, potable water, etc.) or of elementary flows
    techno_transfo_keys: list
        List of all keys of activities with reference exchanges that are
        positive water exchanges (i.e. activities that output water)
    techno_treat_keys: list
        List of all keys of activities with reference exchanges that are
        negative water exchanges (i.e. activities that treat water)
    bio_ress_keys: list
        List of all keys of water elementary flows from nature used by
        activities in database
    bio_emission_keys: list
        List of all keys of water elementary flows to nature used by
        activities in database
    database_name: string
        Name of the LCI database in the brightway2 project
    biosphere: string, default='biosphere3'
        Name of the biosphere database in the brighway2 database
    group: string, default='water'
        Name of the parameter group name. Used in the generation of samples.
    matrix_indices: list
        List of numpy structured arrays containing the matrix indices associated
        with samples
    matrix_samples: list
        List of numpy arrays with samples
    """
    def __init__(self, ecoinvent_version, database_name, biosphere='biosphere3', group="water"):

        # Check that the database exists in the current project
        print("Validating data")
        if database_name not in databases:
            raise ValueError("Database {} not imported".format(database_name))
        self.database_name = database_name
        if biosphere not in databases:
            raise ValueError("Database {} not imported".format(biosphere))
        self.biosphere = biosphere
        self.group = group
        self.matrix_indices = []
        self.matrix_samples = None

        # Check that data is available for current version
        available_versions = ['test_db', '3.4', '3.6'] # todo possibly use migrations for this
        if str(ecoinvent_version) not in available_versions:
            warnings.warn("No data available for version {}, using version {} "
                          "instead, which may result in some errors".format(
                ecoinvent_version, available_versions[-1]
            ))
            self.ecoinvent_version = available_versions[-1]
        else:
            self.ecoinvent_version = str(ecoinvent_version)

        # Identify water exchanges
        print("Getting information on technosphere water exchanges")
        self.techno_transfo_keys, self.techno_treat_keys = self._identify_techno_keys()

        print("Getting information on biosphere water exchanges")
        self.bio_ress_keys, self.bio_emission_keys = self._identify_bio_keys()

        self.all_water_keys = \
            self.techno_transfo_keys + self.techno_treat_keys + \
            self.bio_ress_keys + self.bio_emission_keys

    def add_samples_for_act(self, act_key, iterations):
        """Add samples and indices for given activity

        Actual samples generated by a ActivityWaterBalancer instance.
        The samples and associated matrix indices are formatted for writing
        presamples and are respectively stored in the matrix_samples and
        matrix_indices attributes.

        Parameters:
        -----------
           act_key: tuple
               Key of target activity in database
           iterations: int
               Number of iterations in generated samples
        """
        ab = ActivityWaterBalancer(act_key, self)
        for data in ab.generate_samples(iterations):
            if len(data[1][0])==2:
                for row in data[1]:
                    self.matrix_indices.append((row[0], row[1], 'biosphere'))
            else:
                self.matrix_indices.extend(data[1])
            if self.matrix_samples is None:
                self.matrix_samples = data[0]
            else:
                self.matrix_samples = np.concatenate(
                    [self.matrix_samples, data[0]], axis=0
                )

    def add_samples_for_all_acts(self, iterations):
        """Add samples and indices for all activities in database

        Iterates through all activities in database and calls activity-
        level method add_samples_for_act

        Parameters:
        -----------
           iterations: int
               Number of iterations in generated samples
        """
        act_keys = [act.key for act in Database(self.database_name)]
        for act_key in pyprind.prog_bar(act_keys):
            try:
                self.add_samples_for_act(get_activity(act_key), iterations)
            except Exception as err:
                print(act_key, str(err))

    def create_presamples(self, name=None, id_=None, overwrite=False, dirpath=None,
                            seed='sequential'):
        """Create a presamples package from generated samples

        Parameters
        -----------
           name: str, optional
               A human-readable name for these samples.
           \id_: str, optional
               Unique id for this collection of presamples. Optional, generated automatically if not set.
           overwrite: bool, default=False
               If True, replace an existing presamples package with the same ``\id_`` if it exists.
           dirpath: str, optional
               An optional directory path where presamples can be created. If None, a subdirectory in the ``project`` folder.
           seed: {None, int, "sequential"}, optional, default="sequential"
               Seed used by indexer to return array columns in random order. Can be an integer, "sequential" or None.
        """
        if not all([self.matrix_samples is not None, self.matrix_indices]):
            warnings.warn("No presamples created because there were no matrix data. "
                      "Make sure to run `add_samples_for_all_acts` or "
                      "`add_samples_for_act` for a set of acts first.")
            return

        id_, dirpath = create_presamples_package(
            matrix_data=split_inventory_presamples(self.matrix_samples, self.matrix_indices),
            name=name, id_=id_, overwrite=overwrite, dirpath=dirpath, seed=seed)
        print("Presamples with id_ {} written at {}".format(id_, dirpath))
        return id_, dirpath

    def _identify_bio_keys(self):
        """Identify keys of water biosphere exchanges to consider in balancing"""

        bio_loaded = Database(self.biosphere).load()
        input_bio_keys = []
        output_bio_keys = []
        for ef_key, ef in pyprind.prog_bar(bio_loaded.items()):
            if not "Water" in ef['name']:
                continue
            if not self._check_bio_exc_used_by_database(ef_key):
                continue
            if ef.get('type') == 'natural resource':
                input_bio_keys.append(ef_key)
            elif ef.get('type') == 'emission':
                output_bio_keys.append(ef_key)
            else:
                warnings.warn("Elementary flow type not understood for {}".format(ef))
        return input_bio_keys, output_bio_keys

    def _check_bio_exc_used_by_database(self, ef_key):
        """ Identify if biosphere exchanges used in database"""

        q = ExchangeDataset.select().where(ExchangeDataset.input_code == ef_key[1])
        if len(q) == 0:
            return False
        q2 = q.select().where(ExchangeDataset.output_database == self.database_name)
        if len(q2) == 0:
            return False
        return True

    def _identify_techno_keys(self):
        """Identify keys of activities with water production exchanges

         These should be considered in balancing. Keys are grouped by activities
         associated with input exchanges (e.g. wastewater treatment) and
         output exchanges (e.g. potable water)
         """
        names_file = Path(__file__).parents[0]/'data'/'water_intermediary_exchange_names.json'
        if not names_file.is_file():
            raise FileNotFoundError("Could not find file water_intermediary_exchange_names.json in expected location")
        with open(names_file, "rb") as f:
            techno_product_names_dict = json.load(f)
        techno_product_names = techno_product_names_dict[self.ecoinvent_version]
        techno_treat_keys = []
        techno_transfo_keys = []
        db_loaded = Database(self.database_name).load()
        for act_key, act in pyprind.prog_bar(db_loaded.items()):
            if act['reference product'] in techno_product_names:
                if act['production amount']<0:
                    techno_treat_keys.append(act_key)
                elif act['production amount']>0:
                    techno_transfo_keys.append(act_key)
                else:
                    warnings.warn("Activity {} has a product exchange {} with "
                                  "an amount of 0: skipped".format(
                        act_key,
                        act['reference product']
                    ))
        return techno_transfo_keys, techno_treat_keys
