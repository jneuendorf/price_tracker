from django.contrib import admin

from .models import (
    HtmlNode,
    Page,
    PriceParser,
    RunResult,
    UserAgent,
)
from .models.recipient import CallMeBotRecipient


class CallMeBotRecipientInline(admin.TabularInline):
    model = CallMeBotRecipient.pages.through


class RunResultInline(admin.TabularInline):
    model = RunResult


class HtmlNodeInline(admin.TabularInline):
    model = HtmlNode


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    inlines = [CallMeBotRecipientInline, RunResultInline]
    readonly_fields = ['is_active']
    actions = ["run", "run_test"]

    def run(self, request, queryset):
        for instance in queryset:
            instance.run(force=True)

    def run_test(self, request, queryset):
        for instance in queryset:
            instance.run(force=True, test=True)


@admin.register(RunResult)
class RunResultAdmin(admin.ModelAdmin):
    readonly_fields = ['created_at']
    inlines = [HtmlNodeInline]


@admin.register(HtmlNode)
class HtmlNodeAdmin(admin.ModelAdmin):
    readonly_fields = ['run_result']


admin.site.register(PriceParser)
admin.site.register(CallMeBotRecipient)
admin.site.register(UserAgent)
