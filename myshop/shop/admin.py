from django.contrib import admin
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.admin.views.main import ChangeList
from .models import Customer, Product, Order, Category, Cart
from django.templatetags.static import static
from django.utils.html import format_html

class MyShopAdminSite(admin.AdminSite):
    site_header = 'My Shop Admin'
    site_title = 'My Shop'
    index_title = 'Dashboard'

admin_site = MyShopAdminSite(name='myshopadmin')

@admin.register(Customer, Order, Cart, site=admin_site)
class ShopAdmin(admin.ModelAdmin):
    pass

@admin.register(Category, site=admin_site)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'product_count', 'is_featured', 'display_image')
    list_editable = ('is_featured',)
    search_fields = ('name',)
    actions = ['delete_selected_categories', 'mark_as_featured']
    actions_selection_counter = True

    def name(self, obj):
        return obj.name

    def product_count(self, obj):
        return obj.product_set.count()

    def mark_as_featured(self, request, queryset):
        queryset.update(is_featured=True)

    def display_image(self, obj):
        if obj.image:
            image_url = obj.image.url
            return format_html('<a href="{}" target="_blank"><img src="{}" /></a>', image_url, image_url)
        else:
            placeholder_image = static('/assets/images/category_placeholder.png')
            return format_html('<img src="{}" />', placeholder_image)

    name.short_description = 'Category Name'
    display_image.allow_tags = True
    product_count.short_description = 'Product Count'
    mark_as_featured.short_description = 'Mark as Featured'
    display_image.short_description = 'Image'

    class Media:
        css = {
            'all': ('admin/css/category_admin.css',)
        }


@admin.register(Product, site=admin_site)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_active', 'display_image')
    list_editable = ('is_active',)
    search_fields = ('name', 'category__name')
    actions = ['delete_selected', 'mark_as_active', 'mark_as_inactive']
    actions_selection_counter = True
    list_per_page = 15  # Set the number of products per page

    def category(self, obj):
        return obj.category.name

    def display_image(self, obj):
        if obj.image:
            image_url = obj.image.url
            return format_html('<a href="{}" target="_blank"><img src="{}" /></a>', image_url, image_url)
        else:
            placeholder_image = static('/assets/images/product_placeholder.png')
            return format_html('<img src="{}" />', placeholder_image)

    category.short_description = 'Category'
    display_image.allow_tags = True
    display_image.short_description = 'Image'

    def mark_as_active(self, request, queryset):
        queryset.update(is_active=True)

    def mark_as_inactive(self, request, queryset):
        queryset.update(is_active=False)

    mark_as_active.short_description = 'Mark as Active'
    mark_as_inactive.short_description = 'Mark as Inactive'

    class Media:
        css = {
            'all': ('admin/css/product_admin.css',)
        }

    def get_changelist(self, request, **kwargs):
        """
        Override the get_changelist() method to apply pagination to the product list.
        """
        return ProductChangeList

class ProductChangeList(ChangeList):
    def get_results(self, *args, **kwargs):
        """
        Override the get_results() method to apply pagination to the product list.
        """
        paginator = Paginator(self.queryset, self.list_per_page)
        self.paginator = paginator
        try:
            self.result_list = self.paginator.page(self.page_num + 1).object_list
        except (PageNotAnInteger, EmptyPage):
            self.result_list = self.paginator.page(1).object_list
        super().get_results(*args, **kwargs)