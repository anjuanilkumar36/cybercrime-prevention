
from django.contrib import admin
from django.urls import path

from myapp import views

urlpatterns = [

path('login_get/',views.
     login_get),
path('logout/',views.admin_logout),
path('login_post/',views.login_post),
path('changepw/',views.changepw),
path('changepw_post/',views.changepw_post),
path('forgotpw/',views.forgotpw),
path('forgotpw_post/',views.forgotpw_post),
path('viewuserdetails/',views.viewuserdetails),
path('viewuserdetails_post/',views.viewuserdetails_post),
path('viewcomplaints/',views.viewcomplaints),
path('viewcomplaints_post/',views.viewcomplaints_post),
path('sendreply/<cid>',views.sendreply),
path('sendreply_post/',views.sendreply_post),
path('viewreview/',views.viewreview),
path('viewreview_post/',views.viewreview_post),
path('home/',views.home),

path('user_register/',views.user_register),
path('user_login/',views.user_login),
path('user_viewprofile/',views.user_viewprofile),
path('user_viewprofileandeditprofile/',views.user_viewprofileandeditprofile),
path('user_chnagepassword/',views.user_chnagepassword),
path('useraddpost/',views.useraddpost),
path('user_viewothersusers_post/',views.user_viewothersusers_post),
path('user_viewothersusers/',views.user_viewothersusers),
path('user_sendfriendrequest/',views.user_sendfriendrequest),
path('user_viewotherspost/',views.user_viewotherspost),
path('user_viewapprovedrequest/',views.user_viewapprovedrequest),
path('user_viewfriedrequest/',views.user_viewfriedrequest),
path('user_viewreject/',views.user_viewreject),
path('viewfriends/',views.viewfriends),
path('user_viewfriedlist/',views.user_viewfriedlist),
path('user_viewcomments/',views.user_viewcomments),
path('user_viewcommentsandreply/',views.user_viewcommentsandreply),
path('user_addcomment/',views.user_addcomment),
path('user_viewreply/',views.user_viewreply),
path('user_sendcomplaint/',views.user_sendcomplaint),
path('and_review_rating/',views.and_review_rating),
path('user_chatfromfrieds/',views.user_chatfromfrieds),
path('user_viewownpost/',views.user_viewownpost),
path('user_followback/',views.user_followback),
path('user_remove/',views.user_remove),
path('user_fromremovefromfriendlist/',views.user_fromremovefromfriendlist),
path('postremove/',views.postremove),
path('chat_send/',views.chat_send),
path('chat_view/',views.chat_view_and),
path('likes/',views.likes),
path('user_viewcommentsreply/',views.user_viewcommentsreply),
path('user_addcommentreply/',views.user_addcommentreply),
path('user_viewnotification/',views.user_viewnotification),
path('accept_notification/',views.accept_notification),
path('reject_notification/',views.reject_notification),
path('adviewcomments/', views.adviewcomments),
path('confusionmatrix/', views.confusion_metrix),
path('blockuser/<id>/<pid>/<cid>', views.blockuser),
path('add_public_account/', views.add_public_account),
path('add_private_account/', views.add_private_account),
path('user_viewotherpost/', views.user_viewotherpost),



]
