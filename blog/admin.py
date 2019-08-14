from django.contrib import admin
from .models import Post, Publisher, Author, Book
from django.urls import reverse


class BookAdmin(admin.ModelAdmin):
    fields = ['publication_date', 'title', 'authors', 'publisher']


class AuthorAdmin(admin.ModelAdmin):
    fields = ['salutation', 'name', 'email', 'headshot', 'last_accessed']

class BookInline(admin.StackedInline):
    model = Book
    extra = 0

class BookTabInline(admin.TabularInline):
    model = Book
    extra = 0

class PublisherAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Full Name', {'fields': ['name']}),
        ('Address',
         {'fields': ['address', 'city', 'state_province', 'country']}),
        ('Website', {'fields': ['website']})
    ]
    inlines = [BookInline, BookTabInline]
    list_display = ('name', 'website')
    list_filter = ['name', 'country']
    search_fields = ['city']
    # list_select_related = ('country')
    # prepopulated_fields = {"slug": ("name",)}
    admin.site.register(Post)
    save_as = True
    # view_on_site = True

    def view_on_site(self, obj):
        url = reverse('post_detail', kwargs={'pk': obj.id})
        return 'https://example.com' + url


admin.site.register(Publisher, PublisherAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Book, BookAdmin)

# Register your models here.
