from django.contrib import admin
from .models import *

# Register your models here.


class ChallengeAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'start_date', 'end_date', 'fee', 'captain')
    list_filter = ('captain__nickname',)


class ParticipationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'challenge')
    list_filter = ('user__nickname', 'challenge__title')


class VerificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'participation_id', 'created_at', 'is_verificated')
    list_filter = ('participation_id__user__nickname', 'participation_id__challenge__title')


admin.site.register(Challenge, ChallengeAdmin)
admin.site.register(Participation, ParticipationAdmin)
admin.site.register(Verification, VerificationAdmin)

