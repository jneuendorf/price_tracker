from django.contrib import admin

from .models import PriceParser, Page, RunResult, HtmlNode


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
