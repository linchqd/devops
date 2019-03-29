from django.conf.urls import url, include
from . import views, user, group, permission

urlpatterns = [
    url(r'^user/', include([
        url(r'^login/$', user.UserLoginView.as_view(), name="user_login"),
        url(r'^logout/$', user.UserLogoutView.as_view(), name="user_logout"),
        url(r'^list/$', user.UserListView.as_view(), name="user_list"),
        url(r'^modify/', include([
            url(r'^status/$', user.UserModifyStatusView.as_view(), name="user_modify_status"),
            url(r'^group/$', user.UserJoinGroup.as_view(), name="join_group"),
        ])),
    ])),
    url(r'^group/', include([
        url(r'^list/$', group.GroupListView.as_view(), name="group_list"),
        url(r'^create/$', group.CreateGroupView.as_view(), name="create_group"),
        url(r'^delete/$', group.DeleteGroupView.as_view(), name="delete_group"),
        url(r'^modify/', include([
            url(r'^query/$', group.GroupUserListView.as_view(), name="group_userlist"),
            url(r'^permission/$', group.ModifyGroupPermission.as_view(), name="modify_group_permission"),
        ])),
        url(r'^permissionlist/$', group.GroupPermissioinList.as_view(), name="group_permission_list"),
    ])),
    url(r'^permission/', include([
        url(r'^list/$', permission.PermissionListView.as_view(), name="permission_list"),
        url(r'^add/$', permission.PermissionAddView.as_view(), name="permission_add"),
        url(r'^modify/', include([
            url(r'^displayname/$', permission.ModifyDisplayName.as_view(), name="modify_display_name"),
        ])),
    ])),
]
