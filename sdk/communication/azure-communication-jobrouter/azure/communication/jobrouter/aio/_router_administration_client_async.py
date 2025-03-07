# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from urllib.parse import urlparse
# pylint: disable=unused-import,ungrouped-imports
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Union,
    overload
)

from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.async_paging import AsyncItemPaged
from azure.core.credentials import AzureKeyCredential
from azure.communication.jobrouter._shared.policy import HMACCredentialsPolicy

from .._shared.utils import parse_connection_str

from .._generated._serialization import Serializer  # pylint:disable=protected-access
from .._generated.aio import AzureCommunicationJobRouterService
from .._generated.models import (
    ClassificationPolicy,
    DistributionPolicy,
    ExceptionPolicy,
    ClassificationPolicyItem,
    DistributionPolicyItem,
    ExceptionPolicyItem,
    ExceptionRule,
    BestWorkerMode,
    LongestIdleMode,
    RoundRobinMode,
    StaticQueueSelectorAttachment,
    ConditionalQueueSelectorAttachment,
    RuleEngineQueueSelectorAttachment,
    PassThroughQueueSelectorAttachment,
    WeightedAllocationQueueSelectorAttachment,
    StaticWorkerSelectorAttachment,
    ConditionalWorkerSelectorAttachment,
    RuleEngineWorkerSelectorAttachment,
    PassThroughWorkerSelectorAttachment,
    WeightedAllocationWorkerSelectorAttachment,
    StaticRule,
    ExpressionRule,
    FunctionRule,
    JobQueue,
    JobQueueItem,
)

from .._version import SDK_MONIKER
from .._api_versions import DEFAULT_VERSION

_SERIALIZER = Serializer()


class RouterAdministrationClient(object):  # pylint:disable=too-many-public-methods,too-many-lines
    """A client to interact with the AzureCommunicationService JobRouter service.

    This client provides operations to create, update, list and delete the following entities: classification policy,
    exception policy, distribution policy and queue.

    :param str endpoint:
        The endpoint of the Azure Communication resource.
    :param ~azure.core.credentials.AzureKeyCredential credential:
        The credentials with which to authenticate

    :keyword api_version: Azure Communication Job Router API version.
        Default value is "2022-07-18-preview".
        Note that overriding this default value may result in unsupported behavior.
    """

    def __init__(
            self,
            endpoint: str,
            credential: AzureKeyCredential,
            **kwargs: Any
    ) -> None:
        if not credential:
            raise ValueError("credential can not be None")

        # TokenCredential not supported at the moment
        if hasattr(credential, "get_token"):
            raise TypeError("Unsupported credential: {}. Use an AzureKeyCredential to use HMACCredentialsPolicy"
                            " for authentication".format(type(credential)))

        try:
            if not endpoint.lower().startswith('http'):
                endpoint = "https://" + endpoint
        except AttributeError:
            raise ValueError("Host URL must be a string")

        parsed_url = urlparse(endpoint.rstrip('/'))
        if not parsed_url.netloc:
            raise ValueError("Invalid URL: {}".format(endpoint))

        self._endpoint = endpoint
        self._api_version = kwargs.pop("api_version", DEFAULT_VERSION)
        self._authentication_policy = HMACCredentialsPolicy(endpoint, credential.key, decode_url=True)
        self._client = AzureCommunicationJobRouterService(
            self._endpoint,
            api_version=self._api_version,
            authentication_policy=self._authentication_policy,
            sdk_moniker=SDK_MONIKER,
            **kwargs)

    @classmethod
    def from_connection_string(
            cls,
            conn_str: str,
            **kwargs: Any
    ) -> "RouterAdministrationClient":
        """Create RouterClient from a Connection String.

        :param str conn_str:
            A connection string to an Azure Communication Service resource.
        :return: Instance of RouterAdministrationClient.
        :rtype: ~azure.communication.jobrouter.aio.RouterAdministrationClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_authentication_async.py
                :start-after: [START admin_auth_from_connection_string_async]
                :end-before: [END admin_auth_from_connection_string_async]
                :language: python
                :dedent: 8
                :caption: Authenticating a RouterAdministrationClient from a connection_string
        """
        endpoint, access_key = parse_connection_str(conn_str)

        return cls(endpoint, AzureKeyCredential(access_key), **kwargs)

    # region ExceptionPolicyAio

    @distributed_trace_async
    async def create_exception_policy(
            self,
            exception_policy_id: str,
            exception_policy: ExceptionPolicy,
            **kwargs: Any
    ) -> ExceptionPolicy:
        """Create a new exception policy.

        :param str exception_policy_id: Id of the exception policy.

        :param exception_policy: An instance of exception policy.
        :type exception_policy: ~azure.communication.jobrouter.ExceptionPolicy

        :return: ExceptionPolicy
        :rtype: ~azure.communication.jobrouter.ExceptionPolicy
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/exception_policy_crud_ops_async.py
                :start-after: [START create_exception_policy_async]
                :end-before: [END create_exception_policy_async]
                :language: python
                :dedent: 8
                :caption: Use a RouterAdministrationClient to create an exception policy
        """
        if not exception_policy_id:
            raise ValueError("exception_policy_id cannot be None.")

        return await self._client.job_router_administration.upsert_exception_policy(
            id = exception_policy_id,
            patch = exception_policy,
            **kwargs
        )

    @overload
    async def update_exception_policy(
            self,
            exception_policy_id: str,
            exception_policy: ExceptionPolicy,
            **kwargs: Any
    ) -> ExceptionPolicy:
        """ Update an exception policy.

        :param str exception_policy_id: Id of the exception policy.

        :param exception_policy: An instance of exception policy. This is a positional-only parameter.
          Please provide either this or individual keyword parameters.
        :type exception_policy: ~azure.communication.jobrouter.ExceptionPolicy

        :return: ExceptionPolicy
        :rtype: ~azure.communication.jobrouter.ExceptionPolicy
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """

    @overload
    async def update_exception_policy(
            self,
            exception_policy_id: str,
            *,
            exception_rules: Optional[Dict[str, ExceptionRule]],
            name: Optional[str],
            **kwargs: Any
    ) -> ExceptionPolicy:
        """ Update an exception policy.

        :param str exception_policy_id: Id of the exception policy.

        :keyword exception_rules: (Optional) A dictionary collection of exception rules on the exception
          policy. Key is the Id of each exception rule.
        :paramtype exception_rules: Optional[Dict[str, ~azure.communication.jobrouter.ExceptionRule]]

        :keyword Optional[str] name: The name of this policy.

        :return: ExceptionPolicy
        :rtype: ~azure.communication.jobrouter.ExceptionPolicy
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """

    @distributed_trace_async
    async def update_exception_policy(
            self,
            exception_policy_id: str,
            *args: ExceptionPolicy,
            **kwargs: Any
    ) -> ExceptionPolicy:
        """Update an exception policy.

        :param str exception_policy_id: Id of the exception policy.

        :param exception_policy: An instance of exception policy. This is a positional-only parameter.
          Please provide either this or individual keyword parameters.
        :type exception_policy: ~azure.communication.jobrouter.ExceptionPolicy

        :keyword exception_rules: (Optional) A dictionary collection of exception rules on the exception
          policy. Key is the Id of each exception rule.
        :paramtype exception_rules: Optional[Dict[str, ~azure.communication.jobrouter.ExceptionRule]]

        :keyword Optional[str] name: The name of this policy.

        :keyword exception_policy: An instance of exception policy. Properties defined in
          class instance will not be considered if they are also specified in keyword arguments.
        :paramtype exception_policy: Optional[~azure.communication.jobrouter.ExceptionPolicy]

        :return: ExceptionPolicy
        :rtype: ~azure.communication.jobrouter.ExceptionPolicy
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/exception_policy_crud_ops_async.py
                :start-after: [START update_exception_policy_async]
                :end-before: [END update_exception_policy_async]
                :language: python
                :dedent: 8
                :caption: Use a RouterAdministrationClient to update an exception policy
        """
        if not exception_policy_id:
            raise ValueError("exception_policy_id cannot be None.")

        exception_policy = ExceptionPolicy()
        if len(args) == 1:
            exception_policy = args[0]

        patch = ExceptionPolicy(
            name = kwargs.pop('name', exception_policy.name),
            exception_rules = kwargs.pop('exception_rules', exception_policy.exception_rules)
        )

        return await self._client.job_router_administration.upsert_exception_policy(
            id = exception_policy_id,
            patch = patch,
            **kwargs
        )

    @distributed_trace_async
    async def get_exception_policy(
            self,
            exception_policy_id: str,
            **kwargs: Any
    ) -> ExceptionPolicy:
        """Retrieves an existing distribution policy by Id.

        :param str exception_policy_id: Id of the policy.

        :return: ExceptionPolicy
        :rtype: ~azure.communication.jobrouter.ExceptionPolicy
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/exception_policy_crud_ops_async.py
                :start-after: [START get_exception_policy_async]
                :end-before: [END get_exception_policy_async]
                :language: python
                :dedent: 8
                :caption: Use a RouterAdministrationClient to get an exception policy
        """
        if not exception_policy_id:
            raise ValueError("exception_policy_id cannot be None.")

        return await self._client.job_router_administration.get_exception_policy(
            id = exception_policy_id,
            **kwargs
        )

    @distributed_trace
    def list_exception_policies(
            self,
            **kwargs: Any
    ) -> AsyncItemPaged[ExceptionPolicyItem]:
        """Retrieves existing exception policies.

        :keyword Optional[int] results_per_page: The maximum number of results to be returned per page.

        :return: An iterator like instance of ExceptionPolicyItem
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.communication.jobrouter.ExceptionPolicyItem]
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/exception_policy_crud_ops_async.py
                :start-after: [START list_exception_policies_async]
                :end-before: [END list_exception_policies_async]
                :language: python
                :dedent: 8
                :caption: Use a RouterAdministrationClient to list exception policies

        .. admonition:: Example:

            .. literalinclude:: ../samples/exception_policy_crud_ops_async.py
                :start-after: [START list_exception_policies_batched_async]
                :end-before: [END list_exception_policies_batched_async]
                :language: python
                :dedent: 8
                :caption: Use a RouterAdministrationClient to list exception policies in batches
        """

        results_per_page = kwargs.pop("results_per_page", None)

        params = {}
        if results_per_page is not None:
            params['maxpagesize'] = _SERIALIZER.query("maxpagesize", results_per_page, 'int')

        return self._client.job_router_administration.list_exception_policies(
            params = params,
            **kwargs
        )

    @distributed_trace_async
    async def delete_exception_policy(
            self,
            exception_policy_id: str,
            **kwargs: Any
    ) -> None:
        """Delete an exception policy by Id.

        :param str exception_policy_id: Id of the policy to delete.
        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/exception_policy_crud_ops_async.py
                :start-after: [START delete_exception_policy_async]
                :end-before: [END delete_exception_policy_async]
                :language: python
                :dedent: 8
                :caption: Use a RouterAdministrationClient to delete an exception policy
        """

        if not exception_policy_id:
            raise ValueError("exception_policy_id cannot be None.")

        return await self._client.job_router_administration.delete_exception_policy(
            id = exception_policy_id,
            **kwargs
        )

    # endregion ExceptionPolicyAio

    # region DistributionPolicyAio

    @distributed_trace_async
    async def create_distribution_policy(
            self,
            distribution_policy_id: str,
            distribution_policy: DistributionPolicy,
            **kwargs: Any
    ) -> DistributionPolicy:
        """Create a new distribution policy.

        :param str distribution_policy_id: Id of the distribution policy.

        :param distribution_policy: An instance of distribution policy.
        :type distribution_policy: ~azure.communication.jobrouter.DistributionPolicy

        :return: DistributionPolicy
        :rtype: ~azure.communication.jobrouter.DistributionPolicy
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/distribution_policy_crud_ops_async.py
                :start-after: [START create_distribution_policy_async]
                :end-before: [END create_distribution_policy_async]
                :language: python
                :dedent: 8
                :caption: Use a RouterAdministrationClient to create a distribution policy
        """
        if not distribution_policy_id:
            raise ValueError("distribution_policy_id cannot be None.")

        return await self._client.job_router_administration.upsert_distribution_policy(
            id = distribution_policy_id,
            patch = distribution_policy,
            **kwargs
        )

    @overload
    async def update_distribution_policy(
            self,
            distribution_policy_id: str,
            distribution_policy: DistributionPolicy,
            **kwargs: Any
    ) -> DistributionPolicy:
        """ Update a distribution policy.

        :param str distribution_policy_id: Id of the distribution policy.

        :param distribution_policy: An instance of distribution policy. This is a positional-only parameter.
          Please provide either this or individual keyword parameters.
        :type distribution_policy: ~azure.communication.jobrouter.DistributionPolicy

        :return: DistributionPolicy
        :rtype: ~azure.communication.jobrouter.DistributionPolicy
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """

    @overload
    async def update_distribution_policy(
            self,
            distribution_policy_id: str,
            *,
            name: Optional[str],
            offer_ttl_seconds: Optional[float],
            mode: Optional[Union[BestWorkerMode, LongestIdleMode, RoundRobinMode]],
            **kwargs: Any
    ) -> DistributionPolicy:
        """ Update a distribution policy.

        :param str distribution_policy_id: Id of the distribution policy.

        :keyword Optional[float] offer_ttl_seconds: The expiry time of any offers created under this policy will
          be governed by the offer time to live.

        :keyword mode: Specified distribution mode
        :paramtype mode: Optional[Union[~azure.communication.jobrouter.BestWorkerMode,
            ~azure.communication.jobrouter.LongestIdleMode, ~azure.communication.jobrouter.RoundRobinMode]]

        :keyword Optional[str] name: The name of this policy.

        :return: DistributionPolicy
        :rtype: ~azure.communication.jobrouter.DistributionPolicy
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """

    @distributed_trace_async
    async def update_distribution_policy(
            self,
            distribution_policy_id: str,
            *args: DistributionPolicy,
            **kwargs: Any
    ) -> DistributionPolicy:
        """Update a distribution policy.

        :param str distribution_policy_id: Id of the distribution policy.

        :param distribution_policy: An instance of distribution policy. This is a positional-only parameter.
          Please provide either this or individual keyword parameters.
        :type distribution_policy: ~azure.communication.jobrouter.DistributionPolicy

        :keyword Optional[float] offer_ttl_seconds: The expiry time of any offers created under this policy will
          be governed by the offer time to live.

        :keyword mode: Specified distribution mode
        :paramtype mode: Optional[Union[~azure.communication.jobrouter.BestWorkerMode,
            ~azure.communication.jobrouter.LongestIdleMode, ~azure.communication.jobrouter.RoundRobinMode]]

        :keyword Optional[str] name: The name of this policy.

        :keyword distribution_policy: An instance of distribution policy. Properties defined in
            class instance will not be considered if they are also specified in keyword arguments.
        :paramtype distribution_policy: Optional[~azure.communication.jobrouter.DistributionPolicy]

        :return: DistributionPolicy
        :rtype: ~azure.communication.jobrouter.DistributionPolicy
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/distribution_policy_crud_ops_async.py
                :start-after: [START update_distribution_policy_async]
                :end-before: [END update_distribution_policy_async]
                :language: python
                :dedent: 8
                :caption: Use a RouterAdministrationClient to update a distribution policy
        """
        if not distribution_policy_id:
            raise ValueError("distribution_policy_id cannot be None.")

        distribution_policy = DistributionPolicy()
        if len(args) == 1:
            distribution_policy = args[0]

        patch = DistributionPolicy(
            name = kwargs.pop("name", distribution_policy.name),
            offer_ttl_seconds = kwargs.pop("offer_ttl_seconds", distribution_policy.offer_ttl_seconds),
            mode = kwargs.pop("mode", distribution_policy.mode)
        )

        return await self._client.job_router_administration.upsert_distribution_policy(
            id = distribution_policy_id,
            patch = patch,
            **kwargs
        )

    @distributed_trace_async
    async def get_distribution_policy(
            self,
            distribution_policy_id: str,
            **kwargs: Any
    ) -> DistributionPolicy:
        """Retrieves an existing distribution policy by Id.

        :param str distribution_policy_id: Id of the policy.

        :return: DistributionPolicy
        :rtype: ~azure.communication.jobrouter.DistributionPolicy
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/distribution_policy_crud_ops_async.py
                :start-after: [START get_distribution_policy_async]
                :end-before: [END get_distribution_policy_async]
                :language: python
                :dedent: 8
                :caption: Use a RouterAdministrationClient to get a distribution policy
        """
        if not distribution_policy_id:
            raise ValueError("distribution_policy_id cannot be None.")

        return await self._client.job_router_administration.get_distribution_policy(
            id = distribution_policy_id,
            **kwargs
        )

    @distributed_trace
    def list_distribution_policies(
            self,
            **kwargs: Any
    ) -> AsyncItemPaged[DistributionPolicyItem]:
        """Retrieves existing distribution policies.

        :keyword Optional[int] results_per_page: The maximum number of results to be returned per page.

        :return: An iterator like instance of DistributionPolicyItem
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.communication.jobrouter.DistributionPolicyItem]
        :raises: ~azure.core.exceptions.HttpResponseError

        .. admonition:: Example:

            .. literalinclude:: ../samples/distribution_policy_crud_ops_async.py
                :start-after: [START list_distribution_policies_async]
                :end-before: [END list_distribution_policies_async]
                :language: python
                :dedent: 8
                :caption: Use a RouterAdministrationClient to list distribution policies

        .. admonition:: Example:

            .. literalinclude:: ../samples/distribution_policy_crud_ops_async.py
                :start-after: [START list_distribution_policies_batched_async]
                :end-before: [END list_distribution_policies_batched_async]
                :language: python
                :dedent: 8
                :caption: Use a RouterAdministrationClient to list distribution policies in batches
        """

        results_per_page = kwargs.pop("results_per_page", None)

        params = {}
        if results_per_page is not None:
            params['maxpagesize'] = _SERIALIZER.query("maxpagesize", results_per_page, 'int')

        return self._client.job_router_administration.list_distribution_policies(
            params = params,
            **kwargs
        )

    @distributed_trace_async
    async def delete_distribution_policy(
            self,
            distribution_policy_id: str,
            **kwargs: Any
    ) -> None:
        """Delete a distribution policy by Id.

        :param str distribution_policy_id: Id of the policy to delete.
        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/distribution_policy_crud_ops_async.py
                :start-after: [START delete_distribution_policy_async]
                :end-before: [END delete_distribution_policy_async]
                :language: python
                :dedent: 8
                :caption: Use a RouterAdministrationClient to delete a distribution policy
        """

        if not distribution_policy_id:
            raise ValueError("id cannot be None.")

        return await self._client.job_router_administration.delete_distribution_policy(
            id = distribution_policy_id,
            **kwargs
        )

    # endregion DistributionPolicyAio

    # region QueueAio

    @distributed_trace_async
    async def create_queue(
            self,
            queue_id: str,
            queue: JobQueue,
            **kwargs: Any
    ) -> JobQueue:
        """Create a job queue

        :param str queue_id: Id of the queue.

        :param queue: An instance of JobQueue.
        :type queue: ~azure.communication.jobrouter.JobQueue

        :return: JobQueue
        :rtype: ~azure.communication.jobrouter.JobQueue
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/job_queue_crud_ops_async.py
                :start-after: [START create_queue_async]
                :end-before: [END create_queue_async]
                :language: python
                :dedent: 8
                :caption: Use a RouterAdministrationClient to create a queue
        """
        if not queue_id:
            raise ValueError("queue_id cannot be None.")

        return await self._client.job_router_administration.upsert_queue(
            id = queue_id,
            patch = queue,
            **kwargs)

    @overload
    async def update_queue(
            self,
            queue_id: str,
            queue: JobQueue,
            **kwargs: Any
    ) -> JobQueue:
        """ Update a job queue

        :param str queue_id: Id of the queue.

        :param queue: An instance of JobQueue. This is a positional-only parameter.
          Please provide either this or individual keyword parameters.
        :type queue: ~azure.communication.jobrouter.JobQueue

        :return: JobQueue
        :rtype: ~azure.communication.jobrouter.JobQueue
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """

    @overload
    async def update_queue(
            self,
            queue_id: str,
            *,
            distribution_policy_id: Optional[str],
            name: Optional[str],
            labels: Optional[Dict[str, Union[int, float, str, bool]]],
            exception_policy_id: Optional[str],
            **kwargs: Any
    ) -> JobQueue:
        """ Update a job queue

        :param str queue_id: Id of the queue.

        :keyword Optional[str] distribution_policy_id: The ID of the distribution policy that will determine
          how a job is distributed to workers.

        :keyword Optional[str] name: The name of this queue.

        :keyword labels: A set of key/value pairs that are
          identifying attributes used by the rules engines to make decisions.
        :paramtype labels: Optional[Dict[str, Union[int, float, str, bool]]]

        :keyword Optional[str] exception_policy_id: The ID of the exception policy that determines various
          job escalation rules.

        :return: JobQueue
        :rtype: ~azure.communication.jobrouter.JobQueue
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """

    @distributed_trace_async
    async def update_queue(
            self,
            queue_id: str,
            *args: JobQueue,
            **kwargs: Any
    ) -> JobQueue:
        """Update a job queue

        :param str queue_id: Id of the queue.

        :param queue: An instance of JobQueue. This is a positional-only parameter.
          Please provide either this or individual keyword parameters.
        :type queue: ~azure.communication.jobrouter.JobQueue

        :keyword Optional[str] distribution_policy_id: The ID of the distribution policy that will determine
          how a job is distributed to workers.

        :keyword Optional[str] name: The name of this queue.

        :keyword labels: A set of key/value pairs that are
          identifying attributes used by the rules engines to make decisions.
        :paramtype labels: Optional[Dict[str, Union[int, float, str, bool]]]

        :keyword Optional[str] exception_policy_id: The ID of the exception policy that determines various
        job escalation rules.

        :return: JobQueue
        :rtype: ~azure.communication.jobrouter.JobQueue
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/job_queue_crud_ops_async.py
                :start-after: [START update_queue_async]
                :end-before: [END update_queue_async]
                :language: python
                :dedent: 8
                :caption: Use a RouterAdministrationClient to update a queue
        """
        if not queue_id:
            raise ValueError("queue_id cannot be None.")

        queue = JobQueue()
        if len(args) == 1:
            queue = args[0]

        patch = JobQueue(
            name = kwargs.pop('name', queue.name),
            distribution_policy_id = kwargs.pop('distribution_policy_id', queue.distribution_policy_id),
            labels = kwargs.pop('labels', queue.labels),
            exception_policy_id = kwargs.pop('exception_policy_id', queue.exception_policy_id)
        )

        return await self._client.job_router_administration.upsert_queue(
            id = queue_id,
            patch = patch,
            **kwargs)

    @distributed_trace_async
    async def get_queue(
            self,
            queue_id: str,
            **kwargs: Any
    ) -> JobQueue:
        """Retrieves an existing queue by Id.

        :param str queue_id: Id of the queue.

        :return: JobQueue
        :rtype: ~azure.communication.jobrouter.JobQueue
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/job_queue_crud_ops_async.py
                :start-after: [START get_queue_async]
                :end-before: [END get_queue_async]
                :language: python
                :dedent: 8
                :caption: Use a RouterAdministrationClient to get a queue
        """
        if not queue_id:
            raise ValueError("queue_id cannot be None.")

        return await self._client.job_router_administration.get_queue(
            id = queue_id,
            **kwargs
        )

    @distributed_trace
    def list_queues(
            self,
            **kwargs: Any
    ) -> AsyncItemPaged[JobQueueItem]:
        """Retrieves existing queues.

        :keyword Optional[int] results_per_page: The maximum number of results to be returned per page.

        :return: An iterator like instance of JobQueueItem
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.communication.jobrouter.JobQueueItem]
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/job_queue_crud_ops_async.py
                :start-after: [START list_queues_async]
                :end-before: [END list_queues_async]
                :language: python
                :dedent: 8
                :caption: Use a RouterAdministrationClient to list queues

        .. admonition:: Example:

            .. literalinclude:: ../samples/job_queue_crud_ops_async.py
                :start-after: [START list_queues_batched_async]
                :end-before: [END list_queues_batched_async]
                :language: python
                :dedent: 8
                :caption: Use a RouterAdministrationClient to list queues in batches
        """

        results_per_page = kwargs.pop("results_per_page", None)

        params = {}
        if results_per_page is not None:
            params['maxpagesize'] = _SERIALIZER.query("maxpagesize", results_per_page, 'int')

        return self._client.job_router_administration.list_queues(
            params = params,
            **kwargs
        )

    @distributed_trace_async
    async def delete_queue(
            self,
            queue_id: str,
            **kwargs: Any
    ) -> None:
        """Deletes a queue by Id.

        :param str queue_id: Id of the queue to delete.
        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/job_queue_crud_ops_async.py
                :start-after: [START delete_queue_async]
                :end-before: [END delete_queue_async]
                :language: python
                :dedent: 8
                :caption: Use a RouterAdministrationClient to delete a queue
        """

        if not queue_id:
            raise ValueError("queue_id cannot be None.")

        return await self._client.job_router_administration.delete_queue(
            id = queue_id,
            **kwargs
        )

    # endregion QueueAio

    # region ClassificationPolicyAio

    @distributed_trace_async
    async def create_classification_policy(
            self,
            classification_policy_id: str,
            classification_policy: ClassificationPolicy,
            **kwargs: Any
    ) -> ClassificationPolicy:
        """ Create a classification policy

        :param str classification_policy_id: Id of the classification policy.

        :param classification_policy: An instance of Classification policy.
        :type classification_policy: ~azure.communication.jobrouter.ClassificationPolicy

        :return: ClassificationPolicy
        :rtype: ~azure.communication.jobrouter.ClassificationPolicy
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/classification_policy_crud_ops_async.py
                :start-after: [START create_classification_policy_async]
                :end-before: [END create_classification_policy_async]
                :language: python
                :dedent: 8
                :caption: Use a RouterAdministrationClient to create a classification policy
        """

        if not classification_policy_id:
            raise ValueError("classification_policy_id cannot be None.")

        return await self._client.job_router_administration.upsert_classification_policy(
            id = classification_policy_id,
            patch = classification_policy,
            **kwargs)

    @overload
    async def update_classification_policy(
            self,
            classification_policy_id: str,
            classification_policy: ClassificationPolicy,
            **kwargs: Any
    ) -> ClassificationPolicy:
        """ Update a classification policy

        :param str classification_policy_id: Id of the classification policy.

        :param classification_policy: An instance of Classification policy. This is a positional-only
         parameter. Please provide either this or individual keyword parameters.
        :type classification_policy: ~azure.communication.jobrouter.ClassificationPolicy

        :return: ClassificationPolicy
        :rtype: ~azure.communication.jobrouter.ClassificationPolicy
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """

    @overload
    async def update_classification_policy(
            self,
            classification_policy_id: str,
            *,
            name: Optional[str],
            fallback_queue_id: Optional[str],
            queue_selectors: Optional[List[Union[StaticQueueSelectorAttachment, ConditionalQueueSelectorAttachment, RuleEngineQueueSelectorAttachment, PassThroughQueueSelectorAttachment, WeightedAllocationQueueSelectorAttachment]]],  # pylint: disable=line-too-long
            prioritization_rule: Optional[Union[StaticRule, ExpressionRule, FunctionRule]],
            worker_selectors: Optional[List[Union[StaticWorkerSelectorAttachment, ConditionalWorkerSelectorAttachment, RuleEngineWorkerSelectorAttachment, PassThroughWorkerSelectorAttachment, WeightedAllocationWorkerSelectorAttachment]]],  # pylint: disable=line-too-long
            **kwargs: Any
    ) -> ClassificationPolicy:
        """ Update a classification policy

        :param str classification_policy_id: Id of the classification policy.

        :keyword Optional[str] name: Friendly name of this policy.

        :keyword fallback_queue_id: The fallback queue to select if the queue selector doesn't find a match.
        :paramtype fallback_queue_id: Optional[str]

        :keyword queue_selectors: The queue selectors to resolve a queue for a given job.
        :paramtype queue_selectors: Optional[List[Union[~azure.communication.jobrouter.StaticQueueSelectorAttachment,
          ~azure.communication.jobrouter.ConditionalQueueSelectorAttachment,
          ~azure.communication.jobrouter.RuleEngineQueueSelectorAttachment,
          ~azure.communication.jobrouter.PassThroughQueueSelectorAttachment,
          ~azure.communication.jobrouter.WeightedAllocationQueueSelectorAttachment]]]

        :keyword prioritization_rule: The rule to determine a priority score for a given job.
        :paramtype prioritization_rule: Optional[Union[~azure.communication.jobrouter.StaticRule,
          ~azure.communication.jobrouter.ExpressionRule, ~azure.communication.jobrouter.FunctionRule]]

        :keyword worker_selectors: The worker label selectors to attach to a given job.
        :paramtype worker_selectors: Optional[List[Union[~azure.communication.jobrouter.StaticWorkerSelectorAttachment,
          ~azure.communication.jobrouter.ConditionalWorkerSelectorAttachment,
          ~azure.communication.jobrouter.RuleEngineWorkerSelectorAttachment,
          ~azure.communication.jobrouter.PassThroughWorkerSelectorAttachment,
          ~azure.communication.jobrouter.WeightedAllocationWorkerSelectorAttachment]]]

        :return: ClassificationPolicy
        :rtype: ~azure.communication.jobrouter.ClassificationPolicy
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """

    @distributed_trace_async
    async def update_classification_policy(
            self,
            classification_policy_id: str,
            *args: ClassificationPolicy,
            **kwargs: Any
    ) -> ClassificationPolicy:
        """ Update a classification policy

        :param str classification_policy_id: Id of the classification policy.

        :param classification_policy: An instance of Classification policy. This is a positional-only
         parameter. Please provide either this or individual keyword parameters.
        :type classification_policy: ~azure.communication.jobrouter.ClassificationPolicy

        :keyword Optional[str] name: Friendly name of this policy.

        :keyword fallback_queue_id: The fallback queue to select if the queue selector doesn't find a match.
        :paramtype fallback_queue_id: Optional[str]

        :keyword queue_selectors: The queue selectors to resolve a queue for a given job.
        :paramtype queue_selectors: Optional[List[Union[~azure.communication.jobrouter.StaticQueueSelectorAttachment,
          ~azure.communication.jobrouter.ConditionalQueueSelectorAttachment,
          ~azure.communication.jobrouter.RuleEngineQueueSelectorAttachment,
          ~azure.communication.jobrouter.PassThroughQueueSelectorAttachment,
          ~azure.communication.jobrouter.WeightedAllocationQueueSelectorAttachment]]]

        :keyword prioritization_rule: The rule to determine a priority score for a given job.
        :paramtype prioritization_rule: Optional[Union[~azure.communication.jobrouter.StaticRule,
          ~azure.communication.jobrouter.ExpressionRule, ~azure.communication.jobrouter.FunctionRule]]

        :keyword worker_selectors: The worker label selectors to attach to a given job.
        :paramtype worker_selectors: Optional[List[Union[~azure.communication.jobrouter.StaticWorkerSelectorAttachment,
          ~azure.communication.jobrouter.ConditionalWorkerSelectorAttachment,
          ~azure.communication.jobrouter.RuleEngineWorkerSelectorAttachment,
          ~azure.communication.jobrouter.PassThroughWorkerSelectorAttachment,
          ~azure.communication.jobrouter.WeightedAllocationWorkerSelectorAttachment]]]

        :return: ClassificationPolicy
        :rtype: ~azure.communication.jobrouter.ClassificationPolicy
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/classification_policy_crud_ops_async.py
                :start-after: [START update_classification_policy_async]
                :end-before: [END update_classification_policy_async]
                :language: python
                :dedent: 8
                :caption: Use a RouterAdministrationClient to update a classification policy
        """

        if not classification_policy_id:
            raise ValueError("classification_policy_id cannot be None.")

        classification_policy = ClassificationPolicy()
        if len(args) == 1:
            classification_policy = args[0]

        patch = ClassificationPolicy(
            name = kwargs.pop("name", classification_policy.name),
            fallback_queue_id = kwargs.pop("fallback_queue_id", classification_policy.fallback_queue_id),
            queue_selectors = kwargs.pop("queue_selectors", classification_policy.queue_selectors),
            prioritization_rule = kwargs.pop("prioritization_rule", classification_policy.prioritization_rule),
            worker_selectors = kwargs.pop("worker_selectors", classification_policy.worker_selectors)
        )

        return await self._client.job_router_administration.upsert_classification_policy(
            id = classification_policy_id,
            patch = patch,
            **kwargs)

    @distributed_trace_async
    async def get_classification_policy(
            self,
            classification_policy_id: str,
            **kwargs: Any
    ) -> ClassificationPolicy:
        """Retrieves an existing classification policy by Id.

        :param str classification_policy_id: The id of classification policy.

        :return: ClassificationPolicy
        :rtype: ~azure.communication.jobrouter.ClassificationPolicy
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/classification_policy_crud_ops_async.py
                :start-after: [START get_classification_policy_async]
                :end-before: [END get_classification_policy_async]
                :language: python
                :dedent: 8
                :caption: Use a RouterAdministrationClient to get a classification policy
        """
        if not classification_policy_id:
            raise ValueError("classification_policy_id cannot be None.")

        return await self._client.job_router_administration.get_classification_policy(
            classification_policy_id,
            **kwargs)

    @distributed_trace
    def list_classification_policies(
            self,
            **kwargs: Any
    ) -> AsyncItemPaged[ClassificationPolicyItem]:
        """Retrieves existing classification policies.

        :keyword Optional[int] results_per_page: The maximum number of results to be returned per page.

        :return: An iterator like instance of ClassificationPolicyItem
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.communication.jobrouter.ClassificationPolicyItem]
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/classification_policy_crud_ops_async.py
                :start-after: [START list_classification_policies_async]
                :end-before: [END list_classification_policies_async]
                :language: python
                :dedent: 8
                :caption: Use a RouterAdministrationClient to list classification policies

        .. admonition:: Example:

            .. literalinclude:: ../samples/classification_policy_crud_ops_async.py
                :start-after: [START list_classification_policies_batched_async]
                :end-before: [END list_classification_policies_batched_async]
                :language: python
                :dedent: 8
                :caption: Use a RouterAdministrationClient to list classification policies in batches
        """
        results_per_page = kwargs.pop("results_per_page", None)

        params = {}
        if results_per_page is not None:
            params['maxpagesize'] = _SERIALIZER.query("maxpagesize", results_per_page, 'int')

        return self._client.job_router_administration.list_classification_policies(
            params = params,
            **kwargs)

    @distributed_trace_async
    async def delete_classification_policy(
            self,
            classification_policy_id: str,
            **kwargs: Any
    ) -> None:
        """Delete a classification policy by Id.

        :param str classification_policy_id: The id of classification policy.

        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/classification_policy_crud_ops_async.py
                :start-after: [START delete_classification_policy_async]
                :end-before: [END delete_classification_policy_async]
                :language: python
                :dedent: 8
                :caption: Use a RouterAdministrationClient to delete a classification policy
        """
        if not classification_policy_id:
            raise ValueError("classification_policy_id cannot be None.")

        return await self._client.job_router_administration.delete_classification_policy(
            id = classification_policy_id,
            **kwargs)

    # endregion ClassificationPolicyAio

    async def close(self) -> None:
        await self._client.close()

    async def __aenter__(self) -> "RouterAdministrationClient":
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *args) -> None:
        await self._client.__aexit__(*args)
