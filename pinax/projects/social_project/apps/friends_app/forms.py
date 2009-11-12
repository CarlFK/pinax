from django import forms
from django.contrib.auth.models import User

from friends.models import *
from friends.importer import import_vcards

# @@@ move to django-friends when ready

class ImportVCardForm(forms.Form):
    
    vcard_file = forms.FileField(label="vCard File")
    
    def save(self, user):
        imported, total = import_vcards(self.cleaned_data["vcard_file"].content, user)
        return imported, total
        
from friends.forms import InviteFriendForm as friends_InviteFriendForm
from friends.forms import JoinRequestForm as friends_JoinRequestForm

class InviteFriendForm(friends_JoinRequestForm,friends_InviteFriendForm):
    """
    user enters email addres.
    if it belongs to an exising user, 
        the friends_app InviteFriendForm code is used to send a frend invite
    else  
        the friends_app JoinRequestForm code is used to email an join invite
    """

    def clean_to_user(self):
        """
        override the "must be valid user" rule.
        if it isn't, an email will be sent to invite them 
        and the friend link will be setup if they join.
        """
        return self.cleaned_data["to_user"]

    def clean_email(self):
        """
        override this too.
        if it is existing user, then it will send a friend request.
        """
        return self.cleaned_data["email"]

# careful messing with .clean
# current code works around a bug:
# http://code.pinaxproject.com/tasks/task/522/

    def clean(self):
        users=User.objects.filter(email=self.cleaned_data["email"])
        if users:
            self.cleaned_data["to_user"]=users[0].username
            # existing user, check for friend link
            return friends_InviteFriendForm.clean(self)
        else:
            # new user, check for pending invite
            return friends_JoinRequestForm.clean(self)


    def save(self,user):
        if self.cleaned_data["to_user"]:
            # existing user, send friend request
            return friends_InviteFriendForm.save(self)
        else:
            # no user, send invite
            return friends_JoinRequestForm.save(self,user)


            

