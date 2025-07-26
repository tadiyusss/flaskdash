DEFAULT_SETTINGS_CATEGORY = [
    {
        "name": "site_settings",
        "nice_name": "Site Settings",
        "description": "Settings related to the overall site configuration.",
    }
]

DEFAULT_SETTINGS = [
    {
        "key": "site_title",
        "name": "Site Title",
        "value": "FlaskDash",
        "type": "text",
        "description": "The title of your site, displayed in the header.",
        "editable": True,
        "category_name": "site_settings"
    },
    {
        "key": "site_description",
        "name": "Site Description",
        "value": "A simple Flask dashboard application.",
        "type": "textarea",
        "description": "A brief description of your site for SEO purposes.",
        "editable": True,
        "category_name": "site_settings"
    },
    {
        "key": "allow_registration",
        "name": "Allow User Registration",
        "value": False,
        "type": "bool",
        "description": "Enable or disable user registration on the site.",
        "editable": True,
        "category_name": "site_settings"
    },
    {
        "key": "default_language",
        "name": "Default Language",
        "value": "en",
        "type": "select",
        "description": "The default language for the site.",
        "editable": True,
        "choices": [
            {"value": "en", "label": "English"},
            {"value": "es", "label": "Spanish"},
            {"value": "fr", "label": "French"},
            {"value": "de", "label": "German"}
        ],
        "category_name": "site_settings"
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
        "name": "User",
        "description": "Regular user with limited access to features."
    }
]

"""
icon_types: svg, url
"""

DEFAULT_SIDEBAR_ITEMS = [
    {
        "name": "Dashboard",
        "roles": ["*"],
        "items": [
            {
                "name": "Home",
                "icon_type": "svg",
                "icon": "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 20 20' fill='currentColor' class='size-8 text-gray-500 border bg-white rounded-lg p-2 shadow'><path fill-rule='evenodd' d='M9.293 2.293a1 1 0 0 1 1.414 0l7 7A1 1 0 0 1 17 11h-1v6a1 1 0 0 1-1 1h-2a1 1 0 0 1-1-1v-3a1 1 0 0 0-1-1H9a1 1 0 0 0-1 1v3a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1v-6H3a1 1 0 0 1-.707-1.707l7-7Z' clip-rule='evenodd' /></svg>",
                "route": "core.dashboard",
                "roles": ["*"]
            },
            {
                "name": "Profile",
                "icon_type": "svg",
                "icon": "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 20 20' fill='currentColor' class='size-8 text-gray-500 border bg-white rounded-lg p-2 shadow'><path fill-rule='evenodd' d='M18 10a8 8 0 1 1-16 0 8 8 0 0 1 16 0Zm-5.5-2.5a2.5 2.5 0 1 1-5 0 2.5 2.5 0 0 1 5 0ZM10 12a5.99 5.99 0 0 0-4.793 2.39A6.483 6.483 0 0 0 10 16.5a6.483 6.483 0 0 0 4.793-2.11A5.99 5.99 0 0 0 10 12Z' clip-rule='evenodd' /></svg>",
                "route": "core.profile",
                "roles": ["*"]
            },
            {
                "name": "Settings",
                "icon_type": "svg",
                "icon": "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 20 20' fill='currentColor' class='size-8 text-gray-500 border bg-white rounded-lg p-2 shadow'><path fill-rule='evenodd' d='M7.84 1.804A1 1 0 0 1 8.82 1h2.36a1 1 0 0 1 .98.804l.331 1.652a6.993 6.993 0 0 1 1.929 1.115l1.598-.54a1 1 0 0 1 1.186.447l1.18 2.044a1 1 0 0 1-.205 1.251l-1.267 1.113a7.047 7.047 0 0 1 0 2.228l1.267 1.113a1 1 0 0 1 .206 1.25l-1.18 2.045a1 1 0 0 1-1.187.447l-1.598-.54a6.993 6.993 0 0 1-1.929 1.115l-.33 1.652a1 1 0 0 1-.98.804H8.82a1 1 0 0 1-.98-.804l-.331-1.652a6.993 6.993 0 0 1-1.929-1.115l-1.598.54a1 1 0 0 1-1.186-.447l-1.18-2.044a1 1 0 0 1 .205-1.251l1.267-1.114a7.05 7.05 0 0 1 0-2.227L1.821 7.773a1 1 0 0 1-.206-1.25l1.18-2.045a1 1 0 0 1 1.187-.447l1.598.54A6.992 6.992 0 0 1 7.51 3.456l.33-1.652ZM10 13a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z' clip-rule='evenodd' /></svg>",
                "route": "core.settings",
                "roles": ["Administrator"]
            },
            {
                "name": "Users",
                "icon_type": "svg",
                "icon": "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 20 20' fill='currentColor' class='size-8 text-gray-500 border bg-white rounded-lg p-2 shadow'><path d='M10 9a3 3 0 1 0 0-6 3 3 0 0 0 0 6ZM6 8a2 2 0 1 1-4 0 2 2 0 0 1 4 0ZM1.49 15.326a.78.78 0 0 1-.358-.442 3 3 0 0 1 4.308-3.516 6.484 6.484 0 0 0-1.905 3.959c-.023.222-.014.442.025.654a4.97 4.97 0 0 1-2.07-.655ZM16.44 15.98a4.97 4.97 0 0 0 2.07-.654.78.78 0 0 0 .357-.442 3 3 0 0 0-4.308-3.517 6.484 6.484 0 0 1 1.907 3.96 2.32 2.32 0 0 1-.026.654ZM18 8a2 2 0 1 1-4 0 2 2 0 0 1 4 0ZM5.304 16.19a.844.844 0 0 1-.277-.71 5 5 0 0 1 9.947 0 .843.843 0 0 1-.277.71A6.975 6.975 0 0 1 10 18a6.974 6.974 0 0 1-4.696-1.81Z' /></svg>",
                "route": "core.users",
                "roles": ["Administrator"]
            },
            {
                "name": "Extensions",
                "icon_type": "svg",
                "icon": "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 20 20' fill='currentColor' class='size-8 text-gray-500 border bg-white rounded-lg p-2 shadow'><path d='M10.362 1.093a.75.75 0 0 0-.724 0L2.523 5.018 10 9.143l7.477-4.125-7.115-3.925ZM18 6.443l-7.25 4v8.25l6.862-3.786A.75.75 0 0 0 18 14.25V6.443ZM9.25 18.693v-8.25l-7.25-4v7.807a.75.75 0 0 0 .388.657l6.862 3.786Z' /></svg>",
                "route": "core.extensions",
                "roles": ["Administrator"]
            },
            {
                "name": "Logout",
                "icon_type": "svg",
                "icon": "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 20 20' fill='currentColor' class='size-8 text-gray-500 border bg-white rounded-lg p-2 shadow'><path fill-rule='evenodd' d='M3 4.25A2.25 2.25 0 0 1 5.25 2h5.5A2.25 2.25 0 0 1 13 4.25v2a.75.75 0 0 1-1.5 0v-2a.75.75 0 0 0-.75-.75h-5.5a.75.75 0 0 0-.75.75v11.5c0 .414.336.75.75.75h5.5a.75.75 0 0 0 .75-.75v-2a.75.75 0 0 1 1.5 0v2A2.25 2.25 0 0 1 10.75 18h-5.5A2.25 2.25 0 0 1 3 15.75V4.25Z' clip-rule='evenodd' /><path fill-rule='evenodd' d='M19 10a.75.75 0 0 0-.75-.75H8.704l1.048-.943a.75.75 0 1 0-1.004-1.114l-2.5 2.25a.75.75 0 0 0 0 1.114l2.5 2.25a.75.75 0 1 0 1.004-1.114l-1.048-.943h9.546A.75.75 0 0 0 19 10Z' clip-rule='evenodd' /></svg>",
                "route": "core.logout",
                "roles": ["*"]
            }
        ]
    }
]