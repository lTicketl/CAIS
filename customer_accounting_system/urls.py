from django.contrib import admin
from django.urls import path
from accounting_system import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    # ADMIN
    path('admin/', admin.site.urls),
    # AUTH
    path('', auth_views.LoginView.as_view(template_name='accounting_system/auth.html',
                                          redirect_authenticated_user=True), name="login"),
    path('login/', auth_views.LoginView.as_view(template_name='accounting_system/auth.html',
                                                redirect_authenticated_user=True), name="login"),
    path('reg/', views.reg_client, name='registration'),
    path('cl_acc/', views.cl_acc, name='cl_acc'),
    path('auth/', views.auth, name='auth'),
    path('logout/', views.logout_view, name='logout_view'),
    path('main_page/', views.main_page, name='main_page'),
    # CLIENTS
    path('clients/', views.clients, name='clients'),
    path('pay_form/', views.pay_form, name='pay_form'),
    path('pay/', views.pay, name='pay'),
    path('success_pay/', views.success_pay, name='success_pay'),
    path('tech-support-form/', views.tech_support_form, name='tech_support'),
    path('tech-support/', views.tech_support, name='tech_support'),
    path('success_ts/', views.success_ts, name='success_ts'),
    path('add_client_info/', views.add_client_info, name='add_client_info'),
    path('client-profile/', views.client_profile, name='client-profile'),
    path('ts-profile/', views.ts_profile, name='ts-profile'),
    path('close-ts/', views.close_ts, name='close_ts'),
    path('ts-anal/', views.ts_anal, name='ts_anal'),
    path('filter-clients/', views.filter_clients, name='filter-clients'),
    path('filter-ts/', views.filter_ts, name='filter-ts'),
    path('change-user-form/', views.change_user_form, name='change-user-form'),
    path('change-user/', views.change_user, name='change-user'),
    path('change-worker-form/', views.change_worker_form, name='change-user-form'),
    path('change-worker/', views.change_worker, name='change-user-form'),
    # STAFF
    path('staff/', views.ts, name='staff'),
    path('add-manager/', views.add_manager, name='add-manager'),
    path('change-manager/', views.change_manager, name='change-manager'),
    # SERVICE
    path('tel/', views.tel, name='tel'),
    path('tel_sc/', views.tel_sc, name='tel_connect'),
    path('tel_dc/', views.tel_dc, name='tel_disconnect'),
    path('m_lines/', views.m_lines, name='m_lines'),
    path('ml_sc/', views.ml_sc, name='m_lines_connect'),
    path('ml_dc/', views.ml_dc, name='m_lines_disconnect'),
    path('internet/', views.internet, name='internet'),
    path('internet_sc/', views.internet_sc, name='internet_connect'),
    path('internet_dc/', views.internet_dc, name='internet_disconnect'),
    path('security/', views.online_security, name='security'),
    path('security_sc/', views.online_security_sc, name='security_connect'),
    path('security_dc/', views.online_security_dc, name='security_disconnect'),
    path('backup/', views.backup, name='backup'),
    path('backup_sc/', views.backup_sc, name='backup_connect'),
    path('backup_dc/', views.backup_dc, name='backup_disconnect'),
    path('protect/', views.protect, name='protect'),
    path('protect_sc/', views.protect_sc, name='protect_connect'),
    path('protect_dc/', views.protect_dc, name='protect_disconnect'),
    path('support/', views.support, name='support'),
    path('support_sc/', views.support_sc, name='support_connect'),
    path('support_dc/', views.support_dc, name='support_disconnect'),
    path('s_tv/', views.streaming_tv, name='streaming-tv'),
    path('s_tv_sc/', views.streaming_tv_sc, name='streaming-tv_connect'),
    path('s_tv_dc/', views.streaming_tv_dc, name='streaming-tv_disconnect'),
    path('s_mov/', views.streaming_movies, name='s-mov'),
    path('s_mov_sc/', views.streaming_movies_sc, name='s-mov_connect'),
    path('s_mov_dc/', views.streaming_movies_dc, name='s-mov_connect'),
    path('success_sc/', views.success_sc, name='success_sc'),
    path('service/', views.service, name='service')
]
