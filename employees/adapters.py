from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.core.exceptions import ImmediateHttpResponse
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class MicrosoftAccountAdapter(DefaultSocialAccountAdapter):

    def is_open_for_signup(self, request, sociallogin):
        """
        يسمح بإنشاء حساب "اجتماعي" فقط إذا كان البريد الإلكتروني موجوداً مسبقاً في قاعدة بيانات الموظفين.
        """
        email = (
            sociallogin.user.email
            or sociallogin.account.extra_data.get("mail")
            or sociallogin.account.extra_data.get("userPrincipalName")
        )

        if email:
            exists = User.objects.filter(email__iexact=email).exists()
            if exists:
                return True

        return False

    def pre_social_login(self, request, sociallogin):
        """
        يتم استدعاؤها قبل تسجيل الدخول للربط التلقائي أو إظهار رسائل الخطأ المترجمة.
        """
        # إذا كان الحساب مرتبطاً بالفعل في قاعدة البيانات، لا نفعل شيئاً
        if sociallogin.is_existing:
            return

        # جلب الإيميل من بيانات مايكروسوفت
        email = (
            sociallogin.user.email
            or sociallogin.account.extra_data.get("mail")
            or sociallogin.account.extra_data.get("userPrincipalName")
        )

        # 1. حالة عدم وجود إيميل في حساب مايكروسوفت
        if not email:
            messages.error(
                request,
                _("Microsoft account did not provide an email address.")
            )
            raise ImmediateHttpResponse(redirect("account_login"))

        try:
            # 2. محاولة إيجاد الموظف وربط حسابه يدوياً
            user = User.objects.get(email__iexact=email)
            sociallogin.connect(request, user)

        except User.DoesNotExist:
            # 3. حالة الإيميل غير مسجل في قاعدة بياناتنا
            messages.error(
                request,
                _("No account registered with this email (%(email)s). Please contact administration.") % {'email': email}
            )
            raise ImmediateHttpResponse(redirect("account_login"))

