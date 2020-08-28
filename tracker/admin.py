from django.contrib import admin

from .models import Page, RunResult, HtmlNode


class RunResultInline(admin.TabularInline):
    model = RunResult


class HtmlNodeInline(admin.TabularInline):
    model = HtmlNode


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    # list_display = []
    # list_filter = []
    inlines = [RunResultInline]
    readonly_fields = ['is_active']


@admin.register(RunResult)
class RunResultAdmin(admin.ModelAdmin):
    inlines = [HtmlNodeInline]
