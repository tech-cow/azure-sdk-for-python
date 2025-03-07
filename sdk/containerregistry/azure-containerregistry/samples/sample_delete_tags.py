# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_delete_tags.py

DESCRIPTION:
    This sample demonstrates deleting all but the most recent three tags for each repository.

USAGE:
    python sample_delete_tags.py

    Set the environment variables with your own values before running the sample:
    1) CONTAINERREGISTRY_ENDPOINT - The URL of you Container Registry account

    This sample assumes your registry has at least one repository with more than three tags.
"""
import os
from dotenv import find_dotenv, load_dotenv
from azure.containerregistry import ContainerRegistryClient, ArtifactTagOrder
from sample_utilities import load_registry, get_authority, get_audience, get_credential


class DeleteTags(object):
    def __init__(self):
        load_dotenv(find_dotenv())
        self.endpoint = os.environ.get("CONTAINERREGISTRY_ENDPOINT")
        self.authority = get_authority(self.endpoint)
        self.audience = get_audience(self.authority)
        self.credential = get_credential(
            self.authority, exclude_environment_credential=True
        )

    def delete_tags(self):
        load_registry()
        with ContainerRegistryClient(self.endpoint, self.credential, audience=self.audience) as client:
            # [START list_repository_names]
            for repository in client.list_repository_names():
                print(repository)
                # [END list_repository_names]

                # Keep the three most recent tags, delete everything else
                tag_count = 0
                for tag in client.list_tag_properties(
                    repository, order_by=ArtifactTagOrder.LAST_UPDATED_ON_DESCENDING
                ):
                    tag_count += 1
                    if tag_count > 3:
                        print(f"Deleting {repository}:{tag.name}")
                        client.delete_tag(repository, tag.name)


if __name__ == "__main__":
    sample = DeleteTags()
    sample.delete_tags()
