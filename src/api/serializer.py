from rest_framework import serializers


from django.contrib.auth.models import User

from inventory.models import Collaborator
from core.db.manager import DataHubManager


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'last_login', 'email')


class DataHubSerializer(object):

    def __init__(self, username, repo_base):
        self.username = username
        self.repo_base = repo_base
        self.manager = DataHubManager(
            user=self.username, repo_base=self.repo_base)


class RepoSerializer(DataHubSerializer):

    def create_repo(self, repo_name):
        success = self.manager.create_repo(repo_name)
        return success

    def delete_repo(self, repo_name, force=True):
        success = self.manager.delete_repo(repo=repo_name, force=force)
        return success

    def rename_repo(self, repo, new_name):
        success = self.manager.rename_repo(repo=repo, new_name=new_name)
        return success

    def user_owned_repos(self):
        repos = self.manager.list_repos()
        repos.sort()

        repo_obj_list = []
        for repo in repos:
            collaborators = self.manager.list_collaborators(repo)

            repo_obj_list.append({
                'repo_name': repo,
                'permissions': 'ALL',
                'collaborators': collaborators,
                'owner': self.username
                })

        return {'repos': repo_obj_list}

    def user_accessible_repos(self):
        user_owned_list = self.user_owned_repos()['repos']
        all_collab_list = self.all_collab_repos()['repos']
        return {'repos': user_owned_list + all_collab_list}

    def specific_collab_repos(self, collab_username):
        # get the collaborators
        user = User.objects.get(username=self.username)
        collab_repos = Collaborator.objects.filter(user=user)

        repo_obj_list = []
        for repo in collab_repos:
            collaborators = self.manager.list_collaborators(repo.repo_name)

            repo_obj_list.append({
                'repo_name': repo.repo_name,
                'permissions': repo.permission,
                'owner': repo.repo_base,
                'collaborators': collaborators
                })

        return {'repos': repo_obj_list}

    def all_collab_repos(self):
        collab_repos = self.manager.list_collaborator_repos()

        repo_obj_list = []
        for repo in collab_repos:
            collaborators = self.manager.list_collaborators(repo.repo_name)

            repo_obj_list.append({
                'repo_name': repo.repo_name,
                'privileges': repo.permission,
                'owner': repo.repo_base,
                'collaborators': collaborators
                })

        return {'repos': repo_obj_list}


class CollaboratorSerializer(DataHubSerializer):
    def list_collaborators(self, repo_name):
        collaborators = self.manager.list_collaborators(repo_name)
        return collaborators

    def add_collaborator(self, repo, collaborator, privileges):
        success = self.manager.add_collaborator(
            repo, collaborator, privileges)
        return success

    def remove_collaborator(self, repo, collaborator):
        success = self.manager.delete_collaborator(
            repo, collaborator)
        return success


class TableSerializer(DataHubSerializer):

    def create_table(self, repo, table, params):
        self.manager.set_search_paths([repo])
        success = self.manager.create_table(repo, table, params)
        return success

    def list_tables(self, repo):
        tables = self.manager.list_tables(repo)
        return tables

    def describe_table(self, repo, table, detail=False):
        res = self.manager.describe_table(
            repo=repo, table=table, detail=False)

        response = []
        for column in res:
            response_obj = {}
            response_obj['column_name'] = column[0]
            response_obj['data_type'] = column[1]
            response.append(response_obj)
        return response

    def delete_table(self, repo, table, force=False):
        success = self.manager.delete_table(repo, table, force)
        return success

    def export_table(self, repo, table, file_format='CSV', delimiter=',',
                     header=True):

        success = DataHubManager.export_table(
            username=self.username, repo_base=self.repo_base,
            repo=repo, table=table, file_format=file_format,
            delimiter=delimiter, header=header)

        return success


class ViewSerializer(DataHubSerializer):

    def create_view(self, repo, view, query):
        self.manager.set_search_paths([repo])
        success = self.manager.create_view(repo, view, query)
        return success

    def list_views(self, repo):
        views = self.manager.list_views(repo)
        return views

    def describe_view(self, repo, view, detail=False):
        res = self.manager.describe_view(
            repo=repo, view=view, detail=False)

        response = []
        for column in res:
            response_obj = {}
            response_obj['column_name'] = column[0]
            response_obj['data_type'] = column[1]
            response.append(response_obj)
        return response

    def delete_view(self, repo, view, force=False):
        success = self.manager.delete_view(repo, view, force)
        return success

    def export_view(self, repo, view, file_format='CSV', delimiter=',',
                    header=True):

        success = DataHubManager.export_view(
            username=self.username, repo_base=self.repo_base,
            repo=repo, view=view, file_format=file_format,
            delimiter=delimiter, header=header)

        return success


class CardSerializer(DataHubSerializer):

    def list_cards(self, repo):
        return self.manager.list_repo_cards(repo)

    def describe_card(self, repo, card_name):
        card = self.manager.get_card(repo, card_name)
        res = {}
        res['timestamp'] = card.timestamp
        res['query'] = card.query
        return res

    def create_card(self, repo, query, card_name):
        self.manager.set_search_paths([repo])
        return self.manager.create_card(repo, query, card_name)

    def delete_card(self, repo, card_name):
        return self.manager.delete_card(repo, card_name)

    def export_card(self, repo, card_name, file_format='CSV'):
        self.manager.set_search_paths([repo])
        return self.manager.export_card(repo, card_name, file_format)


class FileSerializer(DataHubSerializer):

    def list_files(self, repo):
        return self.manager.list_repo_files(repo)

    def upload_file(self, repo, file):
        return self.manager.save_file(repo, file)

    def delete_file(self, repo, file_name):
        return self.manager.delete_file(repo, file_name)

    def get_file(self, repo, file_name):
        return self.manager.get_file(repo, file_name)


class QuerySerializer(DataHubSerializer):

    def execute_query(self, query, repo=None):
        if repo:
            self.manager.set_search_paths([repo])

        result = self.manager.execute_sql(query)

        # rename the tuples key to rows
        result['rows'] = result.pop('tuples', None)
        result['columns'] = result.pop('fields', None)

        return result
