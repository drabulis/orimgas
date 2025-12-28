# Bootstrap 5 Implementation Guide

## Files Created

### 1. Base Template
- **File**: `orimgasapp/templates/base_bootstrap.html`
- **Purpose**: New Bootstrap 5 base template (original `base.html` untouched)
- **Features**:
  - Responsive navigation with mobile hamburger menu
  - Bootstrap 5.3.2 CSS/JS
  - Bootstrap Icons
  - jQuery UI datepicker (compatible with existing forms)
  - Language switcher in user dropdown
  - Sticky navigation
  - Footer
  - Toast notifications for messages

### 2. Menu/Dashboard Template
- **File**: `orimgasapp/templates/menu_bootstrap.html`
- **Purpose**: Example Bootstrap implementation of main dashboard
- **Features**:
  - Statistics cards (total, signed, pending, expired instructions)
  - Quick action cards with icons
  - Responsive grid (4 columns desktop, 2 tablet, 1 mobile)
  - Recent activity section

## How to Test Bootstrap Version

### Option 1: Test Route (Recommended)
Add a test URL to see Bootstrap version without affecting production:

```python
# In orimgasapp/urls.py, add:
path('menu/bootstrap/', views.MenuBootstrapView.as_view(), name='menu_bootstrap'),
```

Then create the view:
```python
# In orimgasapp/views.py
class MenuBootstrapView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'menu_bootstrap.html'
```

Access at: `http://localhost:8000/main/menu/bootstrap/`

### Option 2: Gradual Migration
Change templates one by one to extend `base_bootstrap.html` instead of `base.html`.

### Option 3: Template Override
Create a new setting in `settings.py`:
```python
USE_BOOTSTRAP = True  # Set to True to use Bootstrap templates
```

## Creating New Bootstrap Templates

### Template Structure
```django
{% extends 'base_bootstrap.html' %}
{% load static %}
{% load i18n %}

{% block title %}Page Title{% endblock %}

{% block content %}
<div class="container-fluid py-4">
    <!-- Your content here -->
</div>
{% endblock %}
```

### Common Bootstrap Components

#### Card with Header
```html
<div class="card">
    <div class="card-header">
        <i class="bi bi-icon-name"></i> Title
    </div>
    <div class="card-body">
        Content
    </div>
</div>
```

#### Responsive Table
```html
<div class="table-responsive">
    <table class="table table-striped table-hover">
        <thead>
            <tr>
                <th>Column 1</th>
                <th>Column 2</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>Data 1</td>
                <td>Data 2</td>
            </tr>
        </tbody>
    </table>
</div>
```

#### Form with Bootstrap
```html
<form method="post">
    {% csrf_token %}
    <div class="mb-3">
        <label for="id_field" class="form-label">Label</label>
        <input type="text" class="form-control" id="id_field" name="field">
    </div>
    <button type="submit" class="btn btn-primary">Submit</button>
</form>
```

## Bootstrap Grid System

### Responsive Columns
```html
<div class="row">
    <div class="col-lg-3 col-md-4 col-sm-6 col-12">
        <!-- Large: 4 columns, Medium: 3 columns, Small: 2 columns, Mobile: 1 column -->
    </div>
</div>
```

### Breakpoints
- `col-12`: Mobile (< 576px) - full width
- `col-sm-6`: Small (≥ 576px) - 2 columns
- `col-md-4`: Medium (≥ 768px) - 3 columns
- `col-lg-3`: Large (≥ 992px) - 4 columns
- `col-xl-2`: Extra large (≥ 1200px) - 6 columns

## Icons Available

Bootstrap Icons included. Examples:
- `<i class="bi bi-person"></i>` - Person
- `<i class="bi bi-file-text"></i>` - Document
- `<i class="bi bi-check-circle"></i>` - Check
- `<i class="bi bi-exclamation-triangle"></i>` - Warning
- `<i class="bi bi-pencil-square"></i>` - Edit
- `<i class="bi bi-trash"></i>` - Delete

Full list: https://icons.getbootstrap.com/

## Utilities

### Spacing
- `mt-3` - margin-top: 1rem
- `mb-4` - margin-bottom: 1.5rem
- `p-3` - padding: 1rem
- `py-4` - padding-top and bottom: 1.5rem

### Colors
- `text-primary`, `text-success`, `text-danger`, `text-warning`, `text-info`
- `bg-primary`, `bg-light`, `bg-dark`
- `border-primary`, `border-success`

### Display
- `d-none` - hide
- `d-block` - show as block
- `d-md-block` - show on medium screens and up
- `d-none d-md-block` - hide on mobile, show on tablet+

## Next Steps to Convert Templates

1. **user_instructions.html** → **user_instructions_bootstrap.html**
   - Convert table to responsive Bootstrap table
   - Add card wrapper
   - Use badges for status

2. **supervisor_edit_user.html** → **supervisor_edit_user_bootstrap.html**
   - Use Bootstrap form classes
   - Multi-column layout on desktop
   - Tabs for different sections

3. **my_company_users.html** → **my_company_users_bootstrap.html**
   - Responsive table
   - Search bar
   - Action buttons

## Advantages Over Current System

✅ **Mobile-first** - Works perfectly on phones/tablets
✅ **Consistent design** - Professional appearance
✅ **No custom CSS needed** - Bootstrap handles styling
✅ **Faster development** - Pre-built components
✅ **Maintained** - Bootstrap is actively updated
✅ **Accessible** - ARIA labels included
✅ **Icon library** - 1800+ icons available

## Rollback Plan

If Bootstrap doesn't work:
1. All original files are untouched
2. Simply use original templates
3. Delete `_bootstrap.html` files
4. No database changes needed

## Testing Checklist

- [ ] Navigation menu works on mobile
- [ ] Forms submit correctly
- [ ] Datepicker works (YYYY-MM-DD format)
- [ ] Tables are scrollable on mobile
- [ ] Language switcher works
- [ ] Logout works
- [ ] All buttons are clickable on mobile
- [ ] Text is readable on small screens

## Support

Bootstrap 5 Documentation: https://getbootstrap.com/docs/5.3/
Bootstrap Icons: https://icons.getbootstrap.com/
