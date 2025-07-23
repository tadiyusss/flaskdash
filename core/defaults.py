DEFAULT_SETTINGS = [
    {
        "key": "site_title",
        "name": "Site Title",
        "value": "FlaskDash",
        "type": "text",
        "description": "The title of your site, displayed in the header.",
        "editable": True
    },
    {
        "key": "site_description",
        "name": "Site Description",
        "value": "A simple Flask dashboard application.",
        "type": "textarea",
        "description": "A brief description of your site for SEO purposes.",
        "editable": True
    }
]

DEFAULT_ROLES = [
    {
        "name": "Administrator",
        "description": "Administrator with full access to all features."
    },
    {   
        "name": "Editor",
        "description": "Editor with access to content management features."
    },
    {
        "name": "Viewer",
        "description": "Viewer with read-only access to content."
    }
]