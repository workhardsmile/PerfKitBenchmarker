# Copyright 2020 PerfKitBenchmarker Authors. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Module containing class for Snowflake EDW service resource hosted on AWS."""

from perfkitbenchmarker import edw_service
from perfkitbenchmarker import flags
from perfkitbenchmarker import providers

# https://docs.snowflake.net/manuals/user-guide/snowsql-config.html#snowsql-config-file
DEFAULT_CONFIG_LOCATION = '~/.snowsql/config'
DEFAULT_CONFIG_FILE = 'snowsql_config'

FLAGS = flags.FLAGS


class Snowflake(edw_service.EdwService):
  """Object representing a Snowflake Data Warehouse Instance hosted on AWS."""
  CLOUD = providers.AWS
  SERVICE_TYPE = 'snowflake_aws'

  def __init__(self, edw_service_spec):
    super(Snowflake, self).__init__(edw_service_spec)
    # As per Snowflake architecture,
    # https://docs.snowflake.net/manuals/user-guide/intro-key-concepts.html#snowflake-architecture  # pylint: disable=line-too-long
    # A snowflake account can host multiple "virtual warehouses", however
    # the current benchmarking is limited to a single "virtual warehouse" as
    # identified by the connection (FLAGS.snowflake_connection) expected to be
    # defined in the config file (either the preprovisioned snowsql_config file
    # or FLAGS.snowflake_snowsql_config_override_file)
    self.named_connection = FLAGS.snowflake_connection

  def IsUserManaged(self, edw_service_spec):
    # TODO(saksena): Remove the assertion after implementing provisioning of
    # virtual warehouses.
    return True

  def _Create(self):
    """Create a Snowflake cluster."""
    raise NotImplementedError

  def _Exists(self):
    """Method to validate the existence of a Snowflake cluster.

    Returns:
      Boolean value indicating the existence of a cluster.
    """
    return True

  def InstallAndAuthenticateRunner(self, vm, benchmark_name):
    """Method to perform installation and authentication of snowsql client.

    SnowSQL is a cli client to submit queries to a Snowflake Warehouse instance.
    https://docs.snowflake.net/manuals/user-guide/snowsql.html

    Args:
      vm: Client vm on which the script will be run.
      benchmark_name: String name of the benchmark, to allow extraction and
        usage of benchmark specific artifacts (certificates, etc.) during client
        vm preparation.
    """
    vm.Install('snowsql')
    vm.Install('openjdk')
    vm.InstallPreprovisionedBenchmarkData(benchmark_name,
                                          ['snowflake-1.0-SNAPSHOT.jar'], '~/')
    if FLAGS.snowflake_snowsql_config_override_file:
      vm.PushFile(FLAGS.snowflake_snowsql_config_override_file,
                  DEFAULT_CONFIG_LOCATION)
    else:
      vm.InstallPreprovisionedBenchmarkData(benchmark_name,
                                            [DEFAULT_CONFIG_FILE], '~/.snowsql')
      vm.RemoteCommand('mv ~/.snowsql/snowsql_config %s' %
                       DEFAULT_CONFIG_LOCATION)

  def RunCommandHelper(self):
    """Snowflake specific run script command components."""
    return '--connection {}'.format(FLAGS.snowflake_connection)

  def _Delete(self):
    """Delete a Snowflake cluster."""
    raise NotImplementedError

  def GetMetadata(self):
    """Return a metadata dictionary of the benchmarked Snowflake cluster."""
    basic_data = super(Snowflake, self).GetMetadata()
    basic_data['snowflake_connection'] = self.named_connection
    return basic_data
