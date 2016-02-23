from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [

    # user
    url(r'^v1/user/$', views.CurrentUser.as_view(), name='user'),
    url(r'^v1/user/repos/$', views.CurrentUserRepos.as_view(),
        name='user_repos'),
    url(r'^v1/repos/$', views.Repos.as_view(),
        name='user_accessible_repos'),

    # repos
    url(r'^v1/repos/(\w+)/(\w+)/$', views.Repo.as_view(),
        name='delete_rename_repo'),
    url(r'^v1/repos/(\w+)/$', views.ReposForUser.as_view(),
        name='collaborator_repos'),

    # collaborators
    url(r'^v1/repos/(\w+)/(\w+)/collaborators/(\w+)/?',
        views.Collaborator.as_view(), name='add_or_remove_collaborator'),
    url(r'^v1/repos/(\w+)/(\w+)/collaborators/?',
        views.Collaborators.as_view(),
        name='list_collaborators'),

    # tables
    url(r'^v1/repos/(\w+)/(\w+)/tables/(\w+)/?',
        views.Table.as_view(), name='view_table_info'),
    url(r'^v1/repos/(\w+)/(\w+)/tables/?',
        views.Tables.as_view(), name='create_or_list_tables'),

    # views
    url(r'^v1/repos/(\w+)/(\w+)/views/(\w+)/?',
        views.View.as_view(), name='view_view_info'),
    url(r'^v1/repos/(\w+)/(\w+)/views/?',
        views.Views.as_view(), name='create_or_list_views'),

    # cards
    url(r'^v1/repos/(\w+)/(\w+)/cards/(\w+)/?$',
        views.Card.as_view(), name='view_card_info'),
    url(r'^v1/repos/(\w+)/(\w+)/cards/?$',
        views.Cards.as_view(), name='create_or_list_cards'),

    # files
    url(r'^v1/repos/(\w+)/(\w+)/files/(\w+\.+\w+)',
        views.File.as_view(), name='download_or_delete_file'),
    url(r'^v1/repos/(\w+)/(\w+)/files/$',
        views.Export.as_view(), name='export_table_or_view'),
    url(r'^v1/repos/(\w+)/(\w+)/files$',
        views.Files.as_view(), name='list_or_upload_file'),

    # query
    url(r'^v1/query/(\w+)/(\w+)/?', views.Query.as_view(),
        name='execute_sql_repo'),
    url(r'^v1/query/(\w+)/?', views.Query.as_view(),
        name='execute_sql'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
