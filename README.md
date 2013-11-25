django-invitation
=================
Forked from https://github.com/lizrice/django-invitation which is forked from http://code.larlet.fr/django-invitation.

### This version has been modified to offer the option of using django-allauth as the authentication backend:
- Does not require any modifications to django-allauth. 
- Utilizes is_open_for_signup method to integrate the invitation system with allauth. 
- Uses the recipient email to bypass email verification in allauth cince we have verified it.
- Stores the invitation recipient in the model to allow tracking & email verification.

V1.2-sp
-------

An attempt to make this work better with allauth. Seems like either allauth changed or the docs for 1.1 were just incomplete.
Lots of weird stuff with changing the key to a tuple and storing that in the DB. Not sure why needed instead of just a string.


V1.1
----
***recipiant added to model (email field):***  
-This allows us to track recipients. For example we may want to email all recipients a few days prior to expiration.  
-It also allows us to pre-populate form data with the recipient email address and validate it.  
-Compatable with null values.  
***session is now passed the invitation_key object instead of just the key value:***  
***create_bulk_invitation:***  
-Default recipient = None  
***send_bulk_invitations:***  
-Includes a recipient for each invitation sent.  
***Backwards compatable:***  
-Including the recipient email address in the invitation url is optional so the upgrade is backwards compatible with 
previously sent invitations using this format.  This will be removed at a later date.  
***includes south migrations:***  

Django Allauth integration
--------------------------

***1)*** Add the setting `INVITATION_USE_ALLAUTH = True` to your settings.

***2)*** in your settings point to a accountadapter.py file licated someplace in your project:  
SOCIALACCOUNT_ADAPTER ="myproject.accountadapter.SocialAccountAdapter"

***3)*** add ALLOW_NEW_REGISTRATIONS = True/False to your settings file:
This setting allows you to block all new registrations even with a valid invitation.

***4)*** accountadapter.py should look someting like this:  

    from allauth.account.adapter import DefaultAccountAdapter
    from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
    from allauth.exceptions import ImmediateHttpResponse
    from allauth.account.utils import setup_user_email
    from django.conf import settings
    from invitation.models import InvitationKey
    from invitation.backends import InvitationBackend
    from django.contrib.auth.models import Group 
    from allauth.account.signals import user_signed_up
    from django.dispatch import receiver 
    from django.views.generic.simple import direct_to_template
    
    class AccountAdapter(DefaultAccountAdapter):
        def is_open_for_signup(self, request):
            
            if getattr(settings, 'ALLOW_NEW_REGISTRATIONS', False):
                if getattr(settings, 'INVITE_MODE', False):
                    invitation_key = request.session.get('invitation_key', False)
                    if invitation_key:
                        if InvitationKey.objects.is_key_valid(invitation_key.key):
                            invitation_email = request.session.get('invitation_email', False)
                            print 'account adapter invitation_email: ',invitation_email
                            self.stash_verified_email(request, invitation_email)
                            return True
                        else:
                            extra_context = request.session.get('invitation_context', {})
                            template_name = 'invitation/wrong_invitation_key.html'
                            raise ImmediateHttpResponse(direct_to_template(request, template_name, extra_context))
                else:
                    return True
            return False
    
        @receiver (user_signed_up)
        def complete_signup(sender, **kwargs):
            user = kwargs.pop('user')
            request = kwargs.pop('request')
            sociallogin = request.session.get('socialaccount_sociallogin', None)
            # Handle user permissions
            user.groups.add(Group.objects.get(name=settings.DEFAULT_USER_GROUP))
            user.save()
            # Handle invitation if required
            if 'invitation_key' in request.session.keys():
                invitation_key = request.session.get('invitation_key', False)
                invitation_key.mark_used(user)
                del request.session['invitation_key']
                del request.session['invitation_email']
                del request.session['invitation_context']
            print(user.username, ": has signed up!")
            
    
    class SocialAccountAdapter(DefaultSocialAccountAdapter):
    
        def pre_social_login(self, request, sociallogin):
            # add sociallogin to session, because sometimes it's not there...
            request.session['socialaccount_sociallogin'] = sociallogin

DOCUMENTATION:django-inviation  
http://code.larlet.fr/django-invitation/wiki/Home
